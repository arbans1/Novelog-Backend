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

-- Novels Table
CREATE TABLE novels (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE novels IS '소설';
COMMENT ON COLUMN novels.id IS '아이디 (기본 키)';
COMMENT ON COLUMN novels.title IS '제목';
COMMENT ON COLUMN novels.description IS '설명';
COMMENT ON COLUMN novels.published_at IS '공개일';
COMMENT ON COLUMN novels.created_at IS '생성일';
COMMENT ON COLUMN novels.updated_at IS '수정일';

-- Chapter Table
CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    novel_id INT NOT NULL REFERENCES novels(id),
    title VARCHAR(255) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE chapters IS '챕터';
COMMENT ON COLUMN chapters.id IS '아이디 (기본 키)';
COMMENT ON COLUMN chapters.novel_id IS '소설 아이디 (외래 키)';
COMMENT ON COLUMN chapters.title IS '제목';
COMMENT ON COLUMN chapters.published_at IS '공개일';
COMMENT ON COLUMN chapters.created_at IS '생성일';
COMMENT ON COLUMN chapters.updated_at IS '수정일';

-- Novel Memos Table
CREATE TABLE novel_memos (
    id SERIAL PRIMARY KEY,
    novel_id INT NOT NULL REFERENCES novels(id),
    user_id INT NOT NULL REFERENCES users(id),
    content TEXT,
    average_star FLOAT,
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE novel_memos IS '소설 메모';
COMMENT ON COLUMN novel_memos.id IS '아이디 (기본 키)';
COMMENT ON COLUMN novel_memos.novel_id IS '소설 아이디 (외래 키)';
COMMENT ON COLUMN novel_memos.user_id IS '사용자 아이디 (외래 키)';
COMMENT ON COLUMN novel_memos.content IS '내용';
COMMENT ON COLUMN novel_memos.average_star IS '평균 별점';
COMMENT ON COLUMN novel_memos.created_at IS '생성일';
COMMENT ON COLUMN novel_memos.updated_at IS '수정일';

-- Chapter Memos Table
CREATE TABLE chapter_memos (
    id SERIAL PRIMARY KEY,
    chapter_id INT NOT NULL REFERENCES chapters(id),
    user_id INT NOT NULL REFERENCES users(id),
    content TEXT,
    star INT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE chapter_memos IS '챕터 메모';
COMMENT ON COLUMN chapter_memos.id IS '아이디 (기본 키)';
COMMENT ON COLUMN chapter_memos.chapter_id IS '챕터 아이디 (외래 키)';
COMMENT ON COLUMN chapter_memos.user_id IS '사용자 아이디 (외래 키)';
COMMENT ON COLUMN chapter_memos.content IS '내용';
COMMENT ON COLUMN chapter_memos.star IS '별점';
COMMENT ON COLUMN chapter_memos.created_at IS '생성일';
COMMENT ON COLUMN chapter_memos.updated_at IS '수정일';
