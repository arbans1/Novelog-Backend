"""로컬 서버 실행을 위한 파일입니다."""
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", port=8000, reload=False)
