-- Создание таблицы exam_results
CREATE TABLE exam_results (
    result_id SERIAL PRIMARY KEY,
    applicant_id INT NOT NULL,
    math_score INT CHECK (math_score >= 0 AND math_score <= 100),
    russian_language_score INT CHECK (russian_language_score >= 0 AND russian_language_score <= 100),
    physics_score INT CHECK (physics_score >= 0 AND physics_score <= 100),
    total_score INT CHECK (total_score >= 0 AND total_score <= 300),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);