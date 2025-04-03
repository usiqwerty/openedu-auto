# OpenEdu API
## get_sequential_block

GET https://courses.openedu.ru/api/courseware/sequence/block-v1:{course_id}+type@sequential+block@{block_id}

Возвращает JSON

```json

{
  "items": [
    {
      "content": "",
      "page_title": "Аннотация",
      "type": "other",
      "id": "block-v1:urfu+HIST+spring_2025+type@vertical+block@c80702303b8e4c33a78e01a4746587ff",
      "bookmarked": false,
      "path": "РАЗДЕЛ 2. НАРОДЫ И ГОСУДАРСТВА НА ТЕРРИТОРИИ СОВРЕМЕННОЙ РОССИИ В ДРЕВНОСТИ. РУСЬ В IX – ПЕРВОЙ ТРЕТИ XIII В. > Аннотация > Аннотация",
      "graded": false,
      "contains_content_type_gated_content": false,
      "href": "",
      "complete": true
    }
  ],
  "element_id": "8a11444c396b49d5b62a5039de2725ed",
  "item_id": "block-v1:urfu+HIST+spring_2025+type@sequential+block@8a11444c396b49d5b62a5039de2725ed",
  "is_time_limited": false,
  "is_proctored": false,
  "position": 1,
  "tag": "sequential",
  "next_url": null,
  "prev_url": null,
  "banner_text": null,
  "save_position": true,
  "show_completion": true,
  "gated_content": {
    "prereq_id": null,
    "prereq_url": null,
    "prereq_section_name": null,
    "gated": false,
    "gated_section_name": "Аннотация"
  },
  "sequence_name": "Аннотация",
  "exclude_units": true,
  "gated_sequence_paywall": null,
  "is_gated_milestone_passed": true,
  "display_name": "Аннотация",
  "format": null,
  "is_hidden_after_due": false
}
```

## publish_completion

Отметить блок как просмотренный

POST https://courses.openedu.ru/courses/course-v1:{course_id}/xblock/{html_block_id}/handler/publish_completion

Требуется заголовок `X-CSRFToken`

Передаётся `{"completion": 1}` в теле запроса

## problem_check

Отправить решение

POST https://courses.openedu.ru/courses/course-v1:{course_id}/xblock/{blk}/handler/xmodule_handler/problem_check

Возвращает JSON с результатами решения
```json
{
  "success": "correct",
  "contents": "тут большой HTML",
  "progress_changed": true,
  "current_score": 3,
  "total_possible": 3,
  "attempts_used": 9
}
```