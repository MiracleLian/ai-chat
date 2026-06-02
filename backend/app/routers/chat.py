"""对话路由 - 发送问题、历史记录、删除记录"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import auth, crud, schemas, database, models, llm

router = APIRouter(prefix="/chat", tags=["对话"])


@router.post("/send", response_model=schemas.ChatOut, summary="发送问题")
async def send_question(
    payload: schemas.ChatCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """发送问题并获取AI回答"""
    answer = await llm.call_llm(payload.question)
    record = crud.create_chat(db, user_id=current_user.id, question=payload.question, answer=answer)
    return record


@router.get("/history", response_model=schemas.ChatHistoryOut, summary="获取历史对话")
def get_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """分页获取当前用户的对话历史"""
    total, records = crud.get_chats_paginated(db, current_user.id, page, page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "records": records,
    }


@router.get("/count", summary="获取对话统计")
def get_chat_count(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """获取当前用户的对话总数"""
    count = crud.get_user_chat_count(db, current_user.id)
    return {"count": count}


@router.delete("/{chat_id}", summary="删除对话记录")
def delete_chat(
    chat_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """删除指定对话记录"""
    record = crud.delete_chat(db, chat_id, current_user.id)
    if not record:
        raise HTTPException(status_code=404, detail="对话记录不存在")
    return {"message": "删除成功"}


@router.post("/batch-delete", summary="批量删除对话记录")
def batch_delete(
    chat_ids: list[int],
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """批量删除对话记录"""
    deleted = crud.delete_chats_batch(db, chat_ids, current_user.id)
    return {"message": f"成功删除 {deleted} 条记录"}
