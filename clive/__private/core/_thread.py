from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor


class CustomThreadPoolExecutor(ThreadPoolExecutor):
    def shutdown(self, wait: bool = True, *, cancel_futures: bool = True) -> None:  # noqa: FBT001, FBT002
        """Change default behavior of ThreadPoolExecutor.shutdown to cancel futures by default."""
        super().shutdown(wait=wait, cancel_futures=cancel_futures)


thread_pool = CustomThreadPoolExecutor(max_workers=4, thread_name_prefix="clive_thread_pool")
