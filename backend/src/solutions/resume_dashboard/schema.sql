-- Token-Gated Resume Dashboard Database Schema

-- Token access management
CREATE TABLE token_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT UNIQUE NOT NULL,
    company TEXT NOT NULL,
    company_name TEXT NOT NULL,
    custom_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP
);

-- Projects portfolio
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    tech_stack JSON,
    github_url TEXT,
    demo_url TEXT,
    impact_score INTEGER DEFAULT 0,
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills and expertise
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    proficiency_level INTEGER CHECK(proficiency_level BETWEEN 1 AND 5),
    years_experience REAL,
    last_used DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tools and technologies used
CREATE TABLE tools_used (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    skill_id INTEGER,
    usage_context TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

-- Work experience
CREATE TABLE work_experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    description TEXT,
    achievements JSON,
    tech_stack JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Education background
CREATE TABLE education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institution TEXT NOT NULL,
    degree TEXT NOT NULL,
    field_of_study TEXT,
    start_date DATE,
    end_date DATE,
    gpa REAL,
    achievements JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback collection
CREATE TABLE feedback_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    token_hash TEXT,
    feedback_type TEXT CHECK(feedback_type IN ('thumbs_up', 'thumbs_down', 'smile', 'frown', 'manual')),
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    page_context TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (token_hash) REFERENCES token_access(token_hash)
);

-- Chat conversation logs
CREATE TABLE chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    token_hash TEXT,
    agent_type TEXT,
    user_message TEXT,
    bot_response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    FOREIGN KEY (token_hash) REFERENCES token_access(token_hash)
);

-- Access tracking
CREATE TABLE access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT,
    ip_address TEXT,
    user_agent TEXT,
    page_accessed TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_duration_ms INTEGER,
    FOREIGN KEY (token_hash) REFERENCES token_access(token_hash)
);

-- API interaction tracking
CREATE TABLE api_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    api_type TEXT NOT NULL,
    endpoint TEXT,
    request_data JSON,
    response_data JSON,
    status_code INTEGER,
    response_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SQL query demonstrations
CREATE TABLE query_demonstrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_name TEXT NOT NULL,
    query_sql TEXT NOT NULL,
    description TEXT,
    category TEXT,
    expected_result_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Publications
CREATE TABLE publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authors TEXT NOT NULL,
    journal TEXT NOT NULL,
    year INTEGER NOT NULL,
    link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personality and soft skills
CREATE TABLE personality (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personality_summary TEXT,
    work_style TEXT,
    strengths JSON,
    personal_values JSON,
    motivations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interests
CREATE TABLE interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interest_name TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Achievements
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    achievement_text TEXT NOT NULL,
    category TEXT,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Certifications
CREATE TABLE certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    certification_name TEXT NOT NULL,
    issuer TEXT NOT NULL,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_token_access_hash ON token_access(token_hash);
CREATE INDEX idx_feedback_session ON feedback_logs(session_id);
CREATE INDEX idx_chat_session ON chat_logs(session_id);
CREATE INDEX idx_access_logs_timestamp ON access_logs(timestamp);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_publications_year ON publications(year);