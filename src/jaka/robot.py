"""
JAKA 机械臂的轻量连接与工具位姿读取。

仅提供只读能力：登录后读取工具位姿，不上电、
不使能、不下发运动指令，适用于手眼标定等需要读取示教位姿的场景。

约定：
    - 位姿格式 ``[x, y, z, rx, ry, rz]``，平移单位 mm，角度单位 deg；
    - 登录使用 SDK 内置的默认管理员账号（JAKA 默认密码 ``jakazuadmin``）。

异常
----
``JakaError``
    所有 JAKA 相关错误的基类（定义于 :mod:`jaka.jaka`）。

使用示例::

    from jaka import JakaRobot

    with JakaRobot("192.168.36.100") as robot:
        t_base_ee, pose = robot.get_tool_pose()
"""

from __future__ import annotations

from types import TracebackType

import numpy as np
from loguru import logger

from .jaka import JakaError, _load_jkrc

# 连接与位姿读取


class JakaRobot:
    """登录 JAKA 机械臂并读取工具位姿（只读，不上电/使能）。"""

    def __init__(self, ip: str) -> None:
        self.ip: str = ip
        self._sdk = _load_jkrc()
        self._robot = self._sdk.RC(ip)
        self._connected = False

    # 上下文管理器
    def __enter__(self) -> JakaRobot:
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            # 绝不从 __del__ 中传播异常。
            pass

    # 公共属性
    @property
    def connected(self) -> bool:
        """若已登录则返回 ``True``。"""
        return self._connected

    def __repr__(self) -> str:
        state = "connected" if self._connected else "disconnected"
        return f"JakaRobot(ip={self.ip!r}, {state})"

    # 连接
    def connect(self) -> None:
        """登录机械臂（使用 SDK 默认管理员账号）。"""
        if self._connected:
            return
        ret = self._robot.login()
        if not _ok(ret):
            raise JakaError(f"JAKA 登录失败: {ret}")
        self._connected = True
        logger.info("已登录 JAKA 机械臂 {}", self.ip)

    def close(self) -> None:
        """登出机械臂（幂等）。"""
        if not self._connected:
            return
        ret = self._robot.logout()
        if not _ok(ret):
            logger.warning("JAKA 登出返回: {}", ret)
        self._connected = False
        logger.info("已登出 JAKA 机械臂 {}", self.ip)

    # 位姿读取
    def get_tool_pose(self) -> list[float]:
        """读取工具位姿，返回 ``pose``。

        返回
        ----
        list[float]
            ``pose``：``[x, y, z, roll, pitch, yaw]``（mm / rad）。
        """
        if not self._connected:
            self.connect()

        ret = self._robot.get_actual_tool_position()
        if not _ok(ret):
            raise JakaError(f"读取工具位姿失败: {ret}")
        pose = [float(value) for value in ret[1]]
        pose[3:] = np.rad2deg(pose[3:]).tolist()
        if len(pose) != 6:
            raise JakaError(f"工具位姿格式异常: {pose}")

        return pose


# 辅助函数


def _ok(ret: object) -> bool:
    """判断 JAKA SDK 返回是否为成功（``ret[0] == 0``）。"""
    return isinstance(ret, (list, tuple)) and len(ret) > 0 and ret[0] == 0
