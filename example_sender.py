import asyncio
import sender
import time
async def main():
    global s
    s = sender.sender()
    print("sender init")
    await s.setup()
    print("sender setup")
    print(f"SlimeVR server is at {s.get_slimevr_ip()}")
    await s.create_imu(1)
    print("sender imu init")
    await s.set_rotation(1,0,0,0)
    print("imu rotation")
    await s.send_reset() # This is a yaw reset

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())
    while True:
        for i in range(360):
            asyncio.run(s.set_rotation(1, i, i, i))
            time.sleep(0.1)