from aiogram import *
from config import *
from language import *
from database import *
from os import path
from datetime import datetime
from os import path
import subprocess, time, os
initDB()

bot = Bot(token = token)
dp = Dispatcher(bot)

@dp.message_handler(commands = ["start"])
async def start(message: types.Message):
	userList(userID = message.from_user.id, timeNow = datetime.now().strftime("%H:%M:%S"), dayNow = datetime.now().strftime("%d.%m.%Y"))
	languageGet = userLanguageGet(userID = message.from_user.id)
	if languageGet == "EN":
		await bot.send_message(message.from_user.id, languageListEN["restartChat"])
	elif languageGet == "RU":
		await bot.send_message(message.from_user.id, languageListRU["restartChat"])
	else:
		keyboardLanguage = types.InlineKeyboardMarkup()
		buttonLanguageEnglish = types.InlineKeyboardButton(text = "English", callback_data = "english")
		buttonLanguageRussian = types.InlineKeyboardButton(text = "Русский", callback_data = "russian")
		keyboardLanguage.add(buttonLanguageEnglish, buttonLanguageRussian)
		await bot.send_message(message.from_user.id, "Choose language!", reply_markup = keyboardLanguage)

@dp.message_handler(commands = ["language"])
async def language(message: types.Message):
	languageGet = userLanguageGet(userID = message.from_user.id)
	keyboardLanguage = types.InlineKeyboardMarkup()
	buttonLanguageEnglish = types.InlineKeyboardButton(text = "English", callback_data = "english")
	buttonLanguageRussian = types.InlineKeyboardButton(text = "Русский", callback_data = "russian")
	keyboardLanguage.add(buttonLanguageEnglish, buttonLanguageRussian)
	if languageGet == "RU":
		textButton = "Выберите язык!"
	else:
		textButton = "Choose language!"
	await bot.send_message(message.from_user.id, textButton, reply_markup = keyboardLanguage)

@dp.message_handler(commands = ["help"])
async def help(message):
	languageGet = userLanguageGet(userID = message.from_user.id)
	if languageGet == "EN":
		bot.send_message(message.from_user.id, languageListEN["helpMessage"])
	elif languageGet == "RU":
		bot.send_message(message.from_user.id, languageListRU["helpMessage"])
	else:
		bot.send_message(message.from_user.id, "Start the dialog with the bot again with the command /start!")

# If a user suddenly sends an photo.
@dp.message_handler(content_types = ["photo"])
async def photo(message):
	languageGet = userLanguageGet(userID = message.from_user.id)
	if languageGet == "EN":
		bot.send_message(message.from_user.id, languageListEN["erorrMessageImage"])
	elif languageGet == "RU":
		bot.send_message(message.from_user.id, languageListRU["erorrMessageImage"])

@dp.message_handler(content_types = ["document"])
async def document(message):
	languageGet = userLanguageGet(userID = message.from_user.id)
	if message.document.file_size <= 20971520:
		file = await bot.get_file(message.document.file_id)
		fileName = file.file_unique_id + file.file_path[-4:]
		await bot.download_file(file.file_path, "documents/" + fileName)
		format = (path.splitext(path.basename(file.file_path))[-1]).lower()
		formats = {".docx", ".doc", ".txt", ".csv", ".html", ".pptx", ".png", ".odt", ".ott", ".xml", ".jpg", ".bmp", ".svg", ".ppt", ".xls", ".xlsx", ".ods"}
		if format in formats:
			timerStart = time.time()
			subprocess.call(["unoconv", "-f", "pdf", "documents/" + fileName])
			timerStop = time.time()
			os.remove("documents/" + fileName)
			if languageGet == "EN":
				text = languageListEN["sendDocument"]
			elif languageGet == "RU":
				text = languageListRU["sendDocument"]
			else:
				bot.send_message(message.from_user.id, "Start the dialog with the bot again with the command /start!")
			await bot.send_chat_action(message.from_user.id, "upload_document")
			await bot.send_document(message.from_user.id, open("documents/" + fileName[:-4] + ".pdf", "rb"), caption = text)
			processing = round(timerStart - timerStop, 6)
			saveFile(userID = message.from_user.id, inputFileSize = file.file_size, outputFileSize = os.path.getsize("documents/" + fileName[:-4] + ".pdf"), timeNow = datetime.now().strftime("%H:%M:%S"), dayNow = datetime.now().strftime("%d.%m.%Y"), processing = processing)
			os.remove("documents/" + fileName[:-4] + ".pdf")
		else:
			if languageGet == "EN":
				await bot.send_message(message.from_user.id, languageListEN["erorrMessageFormat"])
			elif languageGet == "RU":
				await bot.send_message(message.from_user.id, languageListRU["erorrMessageFormat"])
			else:
				await bot.send_message(message.from_user.id, "Start the dialog with the bot again with the command /start!")
	else:
		if languageGet == "EN":
			await bot.send_message(message.from_user.id, languageListEN["erorrMessageSize"])
		elif languageGet == "RU":
			await bot.send_message(message.from_user.id, languageListRU["erorrMessageSize"])
		else:
			await bot.send_message(message.from_user.id, "Start the dialog with the bot again with the command /start!")

@dp.callback_query_handler()
async def language(query: types.CallbackQuery):
	if query.data == "english":
		language = "EN"
		languageList = languageListEN
	elif query.data == "russian":
		language = "RU"
		languageList = languageListRU
	languageGet = userLanguageGet(userID = query.message.chat.id)
	languages = {"EN", "RU"}
	if languageGet in languages:
		userLanguageChange(userID = query.message.chat.id, language = language)
		await bot.edit_message_text(chat_id = query.message.chat.id, message_id = query.message.message_id, text = languageList["languageChanged"])
	else:
		userLanguage(userID = query.message.chat.id, language = language)
		await bot.edit_message_text(chat_id = query.message.chat.id, message_id = query.message.message_id, text = languageList["startChat"])

if __name__ == "__main__":
	executor.start_polling(dp)