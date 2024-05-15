import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI  # pip install openai
from concurrent.futures import ThreadPoolExecutor, as_completed
import textwrap

openai_client = None


def split_long_line_keep_newlines(s: str, n_chars=100) -> str:
    lines = s.split("\n")
    wrapped_lines = [textwrap.fill(line, width=n_chars) for line in lines]
    return "\n".join(wrapped_lines)


system_message = """
You are an exercise grader tasked with evaluating student submissions. 
Setting aside any prior knowledge on the subject and focus solely on the 
student's response and the reference answer provided. 
Your objective is to assess how well the student 
understood the question and accurately addressed it in their response, 
relative to the reference answer.


Question:
<question>
{QUESTION}
</question>

Reference Answer:
<reference_answer>
{REFERENCE_ANSWER}
</reference_answer>

Student's Response:
<response>
{RESPONSE}
</response>

Your feedback should be structured in JSON format, encompassing the following 
keys and associated values:

 - `valid`: one of ["empty", "only irrelevant", "valid"], indicating whether the response is empty or 
    only contains irrelevant information, or is a valid attempt at answering the question.
 
 - `gross mistakes`: one of ["absent", "present"], indicating whether the answer contains any major errors.
 - `gross mistakes explanation`: A brief explanation of any major errors found in the response, 
    formatted as "The student's response contains <major error> which is incorrect:  <explanation>", 
    or "absent" if there are no major errors.

 - `accuracy`: one of ["accurate", "mostly accurate", "mostly inaccurate", 
   "inaccurate"], representing the factual accuracy of the student's response.
 - `accuracy explanation`: A concise explanation of any factual inaccuracies 
   identified, formatted as "The student's stated that: <inaccurate information> 
   The accurate information is: ...", or "accurate" if there 
   are no inaccuracies.

 - `completeness`: one of ["complete", "mostly complete", "partial", 
   "incomplete"], reflecting how comprehensively the student's response covers 
   the required aspects mentioned in the reference answer.
 - `completeness explanation`: A brief explanation of how the response compares 
   to the reference in terms of completeness. Highlight specific areas that were 
   well-covered or omitted. Use "complete" if the response fully matches the 
   reference's scope.

 - `relevance`: one of ["relevant", "mostly relevant", "mostly irrelevant", 
   "irrelevant"], indicating the presence of any irrelevant information in the 
   student's response.
 - `relevance explanation`: A short explanation identifying parts of the response 
   that were off-topic or not pertinent to the question, in the form "The student
    talked about <irrelevant part> which has no relevance to the question. 
    Use "relevant" if all information was on point.
    
 - `overall quality`: one of ['good', 'ok', 'low'], indicating the overall quality of the response. 


"""


def get_grade_from_grading_response(grading_response):
    assert isinstance(grading_response, dict)

    points = 100
    feedback = ""

    validity = grading_response.get("valid", "").lower()
    if validity not in {"valid", "ok"}:
        feedback += f"The student's response validness is not ok. ({validity})"
        points = 0
        return {"grade": points, "feedback": feedback}

    gross_mistakes = grading_response.get("gross mistakes", "absent")
    if gross_mistakes == "present":
        explanation = {
            grading_response.get(
                "gross mistakes explanation", "No explanation provided."
            )
        }
        points -= 20
        feedback += f"\nThe student's response contains gross mistakes: {gross_mistakes}:\n{explanation}.\nReduce 20%"
        feedback += "\n"

    accuracy = grading_response.get("accuracy", "inaccurate")
    accuracy_reduction = {
        "accurate": 0,
        "mostly accurate": 2,
        "mostly inaccurate": 15,
        "inaccurate": 30,
    }[accuracy]
    if accuracy != "accurate":
        feedback += f"\nAccuracy: {accuracy}. "
        feedback += grading_response.get(
            "accuracy explanation", "No explanation provided."
        )
        feedback += f"\nReduce {accuracy_reduction}%\n"
    points -= accuracy_reduction

    completeness = grading_response.get("completeness", "incomplete")
    completeness_reduction = {
        "complete": 0,
        "mostly complete": 2,
        "partial": 10,
        "incomplete": 20,
    }[completeness]
    if completeness != "complete":
        feedback += f"\nCompleteness: {completeness}. "
        feedback += grading_response.get(
            "completeness explanation", "No explanation provided."
        )
        feedback += f"\nReduce {completeness_reduction}%\n"
    points -= completeness_reduction

    irrelevant = grading_response.get("relevance", "irrelevant")
    irrelevant_reduction = {
        "relevant": 0,
        "mostly relevant": 2,
        "mostly irrelevant": 5,
        "irrelevant": 15,
    }[irrelevant]
    if irrelevant != "relevant":
        feedback += f"\nRelevance: {irrelevant}. "
        feedback += grading_response.get(
            "relevance explanation", "No explanation provided."
        )
        feedback += f"\nReduce {irrelevant_reduction}%\n"
    points -= irrelevant_reduction

    overall_quality = grading_response.get("overall quality", "low")
    bonus_overall = {"good": 20, "ok": 10, "low": 0}[overall_quality]
    if points < 100 and bonus_overall:
        points += bonus_overall
        feedback += (
            f"\nOverall quality: {overall_quality}.\nBonus up to {bonus_overall}%\n"
        )
        points = min(100, points)

    points = max(0, points)
    return {"grade": points, "feedback": feedback}


def openai_grade_student_response(question, correct_answer, student_response):
    global openai_client
    if openai_client is None:
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_org_id = os.getenv("OPENAI_ORG_ID", None)
        openai_client = OpenAI(api_key=openai_api_key, organization=openai_org_id)

    formatted_system_message = system_message.format(
        QUESTION=question, REFERENCE_ANSWER=correct_answer, RESPONSE=student_response
    )
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": formatted_system_message},
        ],
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
    )
    # Assuming the grading logic returns JSON as string in the response
    resp = chat_completion.choices[0].message.content
    try:
        grade_info = json.loads(resp)
    except json.JSONDecodeError:
        grade_info = resp
    ret = get_grade_from_grading_response(grade_info)
    return ret


def parallel_grade(attempt_args):
    """
    Wrapper function to call `openai_grade_student_response` with retries.
    """
    question, correct_answer, student_response, n_retries = attempt_args
    for _ in range(n_retries):
        try:
            return openai_grade_student_response(
                question, correct_answer, student_response
            )
        except Exception as e:
            print(f"Error grading response: {e}")
    return None


def grade_student_response(
    question: str,
    correct_answer: str,
    student_response: str,
    n_retries_on_error: int = 3,
    n_grades: int = 3,
    grade_strategy: Literal["best", "worst"] = "best",
    include_correct_answer: bool = True,
    n_jobs: int = 3,
    round_up: bool = True,
) -> dict:
    """
    Grade a student's response to a given question, utilizing the OpenAI API to generate multiple grades
    and selecting the final grade based on the specified strategy. Supports parallel grading.

    Args:
        question (str): The question that was asked to the student.
        correct_answer (str): The reference or correct answer to the question.
        student_response (str): The response provided by the student.
        n_retries_on_error (int): The number of attempts to retry grading if an error occurs. Defaults to 3.
        n_grades (int): The number of grades to generate before deciding on the final grade. Defaults to 3.
        grade_strategy (Literal["best", "worst"]): Strategy to determine the final grade. 'best' for the highest
            grade and 'worst' for the lowest. Defaults to "best".
        include_correct_answer (bool): Whether to include the correct answer in the grading request. Defaults to True.
        n_jobs (int): The number of parallel jobs to use for grading. Defaults to 1.
        round_up (bool): Whether to round up the final grade to the nearest 5. Defaults to True.

    Returns:
        dict: The final grading decision, containing the grade and feedback.
    """
    grades = []
    with ThreadPoolExecutor(max_workers=n_jobs) as executor:
        futures = [
            executor.submit(
                parallel_grade,
                (question, correct_answer, student_response, n_retries_on_error),
            )
            for _ in range(n_grades)
        ]
        for future in as_completed(futures):
            result = future.result()
            if result:
                grades.append(result)

    if not grades:
        raise Exception("Failed to grade after multiple attempts.")

    if grade_strategy == "best":
        final_grade = max(grades, key=lambda x: x["grade"])
    else:  # worst
        final_grade = min(grades, key=lambda x: x["grade"])

    final_grade[
        "more details"
    ] = f'{grade_strategy} of {n_grades} grades: {[g["grade"] for g in grades]}'
    if include_correct_answer:
        final_grade["correct_answer"] = correct_answer

    if round_up:
        grade_now = final_grade["grade"]
        new_grade = (grade_now // 5) * 5
        if new_grade > grade_now:
            final_grade["grade"] = new_grade
            final_grade["feedback"] += f"\n\nRounded up to {new_grade}"

    for k, v in final_grade.items():
        if isinstance(v, str):
            final_grade[k] = split_long_line_keep_newlines(v)

    return final_grade


if __name__ == "__main__":
    # Call the function with the example inputs

    question = "Explain the stark difference between the results of SVD applied on normalized and non-normalized data."
    correct_answer = (
        "The terms 'top K values', 'K values', etc are identical to 'top singular values' 'singular values'"
        "The results of applying SVD on normalized versus non-normalized data show stark differences. "
        "For non-normalized data, where variables can vary widely in scale, the first few top K values "
        "often capture most of the variance. This is because the larger-scale variables disproportionately "
        "influence the variance. Conversely, when SVD is applied to normalized data,  the variance is more "
        "evenly distributed across the top K  values. "
        "As a result, the first few top K values capture a smaller portion of the total variance, "
        "indicating a more balanced representation of the data's underlying structure."
    )
    # print(f"Correct answer:\n{correct_answer}")
    student_responses = [
        """ Yes, there is a difference between the K found in `compute_k_svd_raw` and `compute_k_svd_normalized`.
        -Normalization standardizes the scale of each feature, preventing features with larger scales from dominating the variance calculation.
        -As a result, when using SVD on the normalized dataset, fewer features may be needed to capture the same amount of overall variance.
    
        Difference: 1.The K value obtained from compute_k_svd_raw might be higher than the one from compute_k_svd_normalized.
                    2.Normalization can affect the variance distribution across features.
                      It may result in a more compact representation of the data, requiring
                      fewer features to explain the same amount of variance. 
    
        compute_k_svd_raw:
           This function likely performs SVD on the raw dataset without any normalization.
           The resulting K value represents the number of features (singular values) needed to explain at least 90% 
           of the relative variance in the raw dataset.
    
        compute_k_svd_normalized:
           This function first normalizes each column of the dataset using the normalize_columns function.
           Then, SVD is applied to the normalized dataset to identify the number of features needed to explain at least 90%
           of the relative variance.  
            """,
        """
        The difference between the K values obtained from `compute_k_svd_raw` and `compute_k_svd_normalized` lies in the 
        preprocessing steps applied to the data. 

        In `compute_k_svd_raw`, we directly apply SVD to the raw data without any preprocessing. This means that the 
        variance captured by each feature may vary widely due to differences in the scale and magnitude of the features.

        However, in `compute_k_svd_normalized`, we first normalize each column of the dataset using the `normalize_columns`
        function. This normalization process scales each feature to have a mean of 0 and a standard deviation of 1. By doing 
        so, we ensure that each feature contributes equally to the variance analysis. Therefore, when we apply SVD to the 
        normalized data, the variance captured by each feature is more balanced and consistent.

        As a result, the K value obtained from `compute_k_svd_normalized` may differ from that of `compute_k_svd_raw` 
        because the normalization process affects the relative contribution of each feature to the overall variance 
        explained by the SVD components.
        """,
    ]
    for student_response in student_responses:
        print(f"Student response:\n{student_response}")

        grade_info = grade_student_response(
            question,
            correct_answer,
            student_response,
            include_correct_answer=True,
            round_up=True,
        )
        for k, v in grade_info.items():
            print(f"{k}: >>>>>")
            print(v)

        print("\n")
        print("-" * 100)
