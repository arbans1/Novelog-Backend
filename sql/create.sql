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
    author VARCHAR(255),
    published_at TIMESTAMP WITH TIME ZONE,
    last_updated_at TIMESTAMP WITH TIME ZONE,
    category VARCHAR(20) NOT NULL,
    ridi_id VARCHAR(20) UNIQUE,
    kakao_id VARCHAR(20) UNIQUE,
    series_id VARCHAR(20) UNIQUE,
    munpia_id VARCHAR(20) UNIQUE,
    image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX novels_title_author_idx ON novels(title, author);

COMMENT ON TABLE novels IS '소설';
COMMENT ON COLUMN novels.id IS '아이디 (기본 키)';
COMMENT ON COLUMN novels.title IS '제목';
COMMENT ON COLUMN novels.author IS '작가';
COMMENT ON COLUMN novels.description IS '설명';
COMMENT ON COLUMN novels.published_at IS '공개일';
COMMENT ON COLUMN novels.last_updated_at IS '최종 업데이트일';
COMMENT ON COLUMN novels.category IS '카테고리';
COMMENT ON COLUMN novels.ridi_id IS '리디북스 아이디';
COMMENT ON COLUMN novels.kakao_id IS '카카오 페이지 아이디';
COMMENT ON COLUMN novels.series_id IS '시리즈 아이디';
COMMENT ON COLUMN novels.munpia_id IS '문피아 아이디';
COMMENT ON COLUMN novels.image_url IS '이미지 URL';
COMMENT ON COLUMN novels.created_at IS '생성일';
COMMENT ON COLUMN novels.updated_at IS '수정일';


-- Chapter Table
CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    novel_id INT NOT NULL REFERENCES novels(id),
    chapter_no INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    ridi_id VARCHAR(20) UNIQUE,
    kakao_id VARCHAR(20) UNIQUE,
    series_id VARCHAR(20) UNIQUE,
    munpia_id VARCHAR(20) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX chapters_novel_id_chapter_no_idx ON chapters(novel_id, chapter_no DESC);

COMMENT ON TABLE chapters IS '챕터';
COMMENT ON COLUMN chapters.id IS '아이디 (기본 키)';
COMMENT ON COLUMN chapters.novel_id IS '소설 아이디 (외래 키)';
COMMENT ON COLUMN chapters.chapter_no IS '챕터 번호';
COMMENT ON COLUMN chapters.title IS '제목';
COMMENT ON COLUMN chapters.published_at IS '공개일';
COMMENT ON COLUMN chapters.ridi_id IS '리디북스 아이디';
COMMENT ON COLUMN chapters.kakao_id IS '카카오 페이지 아이디';
COMMENT ON COLUMN chapters.series_id IS '시리즈 아이디';
COMMENT ON COLUMN chapters.munpia_id IS '문피아 아이디';
COMMENT ON COLUMN chapters.created_at IS '생성일';
COMMENT ON COLUMN chapters.updated_at IS '수정일';

-- Novel Memos Table
CREATE TABLE novel_memos (
    novel_id INT NOT NULL REFERENCES novels(id),
    user_id INT NOT NULL REFERENCES users(id),
    content TEXT,
    average_star FLOAT,
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    content_updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (novel_id, user_id)
);

COMMENT ON TABLE novel_memos IS '소설 메모';
COMMENT ON COLUMN novel_memos.novel_id IS '소설 아이디 (외래 키)';
COMMENT ON COLUMN novel_memos.user_id IS '사용자 아이디 (외래 키)';
COMMENT ON COLUMN novel_memos.content IS '내용';
COMMENT ON COLUMN novel_memos.average_star IS '평균 별점';
COMMENT ON COLUMN novel_memos.created_at IS '생성일';
COMMENT ON COLUMN novel_memos.updated_at IS '수정일';
COMMENT ON COLUMN novel_memos.content_updated_at IS '내용 수정일';


-- Chapter Memos Table
CREATE TABLE chapter_memos (
    chapter_id INT NOT NULL REFERENCES chapters(id),
    user_id INT NOT NULL REFERENCES users(id),
    content TEXT,
    star INT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (chapter_id, user_id)
);


COMMENT ON TABLE chapter_memos IS '챕터 메모';
COMMENT ON COLUMN chapter_memos.chapter_id IS '챕터 아이디 (외래 키)';
COMMENT ON COLUMN chapter_memos.user_id IS '사용자 아이디 (외래 키)';
COMMENT ON COLUMN chapter_memos.content IS '내용';
COMMENT ON COLUMN chapter_memos.star IS '별점';
COMMENT ON COLUMN chapter_memos.created_at IS '생성일';
COMMENT ON COLUMN chapter_memos.updated_at IS '수정일';
