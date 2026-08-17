from jaka import JakaRobot

if __name__ == "__main__":
    with JakaRobot("192.168.36.100") as robot:
        print(robot._robot.get_sdk_version())
        print(robot.get_tcp_pose())
