-- Создание таблицы applicants
CREATE TABLE applicants (
    applicant_id SERIAL PRIMARY KEY,
    last_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    school_id INT NOT NULL,
    city_id INT NOT NULL,
    FOREIGN KEY (school_id) REFERENCES schools(school_id),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);
