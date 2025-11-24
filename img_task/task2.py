import asyncio
import aiohttp
import os

def input_url():
	f_name = 'img'
	f_ext = '.jpg'
	counter = 0
	while True:
		f_new = f"{f_name}{counter}{f_ext}"
		if not os.path.exists(f_new):
			return f_new	
		else:
			counter+=1

async def downloader(url, path):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as answer:
			if answer.status == 200:
				image = await answer.read()
				with open(path, 'wb') as file:
					file.write(image)

async def main():
	path = input("path: ").strip()
	while True:
		url = input("url: ")
		f_name = input_url()
		f_path = os.path.join(path, f_name)
		await downloader(url, f_path)
	# await downloader('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQuxeoUNJiwTkjE9HW9wqRPoOdOeaDoxJQiYA&s', './image.jpg')
	
if __name__ == "__main__":
    asyncio.run(main())
