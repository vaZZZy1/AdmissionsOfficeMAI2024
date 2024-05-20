### Схема базы данных в dbdiagram

```
Table cities {
  city_id SERIAL [pk]
  city_name VARCHAR(255)
}

Table schools {
  school_id SERIAL [pk]
  school_name VARCHAR(255)
  city_id INT [ref: > cities.city_id]
}

Table applicants {
  applicant_id SERIAL [pk]
  last_name VARCHAR(255)
  first_name VARCHAR(255)
  middle_name VARCHAR(255)
  school_id INT [ref: > schools.school_id]
  city_id INT [ref: > cities.city_id]
}

Table exam_results {
  result_id SERIAL [pk]
  applicant_id INT [ref: > applicants.applicant_id]
  math_score INT 
  russian_language_score INT
  physics_score INT
  total_score INT
}

Table mood_metrics {
  metric_id SERIAL [pk]
  applicant_id INT [ref: > applicants.applicant_id]
  happiness_score INT
  stress_score INT
  anxiety_score INT
  calmness_score INT
}
```

https://dbdiagram.io/d/664a70fdf84ecd1d2295f249 - ссылка визаулизацию
