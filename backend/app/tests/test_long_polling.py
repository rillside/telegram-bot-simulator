import pytest
import asyncio
from backend.app.bot_api.polling import update_queue_manager

@pytest.mark.asyncio
async def test_update_queue_acknowledgement():
    bot_id = 901
    await update_queue_manager.start_bot(bot_id)

    # Enqueue 3 updates
    await update_queue_manager.enqueue_update(bot_id, {"update_id": 101, "message": {"text": "one"}})
    await update_queue_manager.enqueue_update(bot_id, {"update_id": 102, "message": {"text": "two"}})
    await update_queue_manager.enqueue_update(bot_id, {"update_id": 103, "message": {"text": "three"}})

    # Fetch with offset=102 -> should acknowledge 101 and return 102, 103
    updates = await update_queue_manager.get_updates(bot_id, offset=102, limit=10, timeout=0)
    assert len(updates) == 2
    assert [u["update_id"] for u in updates] == [102, 103]

    # Next fetch with offset=104 -> acknowledges 102 and 103, queue is now empty
    empty_updates = await update_queue_manager.get_updates(bot_id, offset=104, limit=10, timeout=0)
    assert len(empty_updates) == 0

@pytest.mark.asyncio
async def test_long_polling_wait_and_wakeup():
    bot_id = 902
    await update_queue_manager.start_bot(bot_id)

    async def delayed_enqueue():
        await asyncio.sleep(0.3)
        await update_queue_manager.enqueue_update(bot_id, {"update_id": 201, "message": {"text": "wake"}})

    asyncio.create_task(delayed_enqueue())

    # Should wait up to 1s and wake up when update arrives
    updates = await update_queue_manager.get_updates(bot_id, offset=None, limit=10, timeout=1)
    assert len(updates) == 1
    assert updates[0]["update_id"] == 201

@pytest.mark.asyncio
async def test_long_polling_stop_bot_cancellation():
    bot_id = 903
    await update_queue_manager.start_bot(bot_id)

    async def delayed_stop():
        await asyncio.sleep(0.2)
        await update_queue_manager.stop_bot(bot_id)

    asyncio.create_task(delayed_stop())

    # Should return early with empty list when bot is stopped
    updates = await update_queue_manager.get_updates(bot_id, offset=None, limit=10, timeout=5)
    assert updates == []
