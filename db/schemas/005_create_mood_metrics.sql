-- Создание таблицы mood_metrics
CREATE TABLE mood_metrics (
    metric_id SERIAL PRIMARY KEY,
    applicant_id INT NOT NULL,
    happiness_score INT CHECK (happiness_score >= 0 AND happiness_score <= 10),
    stress_score INT CHECK (stress_score >= 0 AND stress_score <= 10),
    anxiety_score INT CHECK (anxiety_score >= 0 AND anxiety_score <= 10),
    calmness_score INT CHECK (calmness_score >= 0 AND calmness_score <= 10),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);
