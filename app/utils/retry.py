import asyncio, logging

async def retry_connect(connect_func, name) :
    for time in range(5) :
        try :
            await connect_func()
            logging.info(f"{name} 연결 : 성공")
            break
        except :
            await asyncio.sleep(pow(2, time))
            logging.info(f"{name} 연결 : 실패, {time+1}번째 시도")
    else :
        raise Exception(f"{name} 연결 : 5번 실패. 연결 시도 중지")