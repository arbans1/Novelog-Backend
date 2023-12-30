-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login_id VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(72) NOT NULL,
    nickname VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE users IS '사용자';
COMMENT ON COLUMN users.id IS '아이디 (기본 키)';
COMMENT ON COLUMN users.login_id IS '이메일';
COMMENT ON COLUMN users.hashed_password IS '해시된 비밀번호';
COMMENT ON COLUMN users.nickname IS '닉네임';
COMMENT ON COLUMN users.is_admin IS '관리자 여부';
COMMENT ON COLUMN users.is_active IS '활성화 여부';
COMMENT ON COLUMN users.created_at IS '생성일';
COMMENT ON COLUMN users.updated_at IS '수정일';
COMMENT ON COLUMN users.deleted_at IS '삭제일';

