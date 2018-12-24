# -*- coding: utf-8 -*-

from line.linepy import *
from gtts import gTTS
from bs4 import BeautifulSoup
from datetime import datetime
from googletrans import Translator
import ast, codecs, json, os, pytz, re, random, requests, sys, time, urllib.parse

listApp = [
	"CHROMEOS\t2.1.5\tHelloWorld\t11.2.5", 
	"DESKTOPWIN\t5.9.2\tHelloWorld\t11.2.5", 
	"DESKTOPMAC\t5.9.2\tHelloWorld\t11.2.5", 
	"IOSIPAD\t8.12.2\tHelloWorld\t11.2.5", 
	"WIN10\t5.5.5\tHelloWorld\t11.2.5"
]
try:
	for app in listApp:
		try:
			try:
				with open("authToken.txt", "r") as token:
					authToken = token.read().replace("\n","")
					if not authToken:
						client = LINE()
						with open("authToken.txt","w") as token:
							token.write(client.authToken)
						continue
					client = LINE(authToken, speedThrift=False, appName=app)
				break
			except Exception as error:
				print(error)
				if error == "REVOKE":
					exit()
				elif "auth" in error:
					continue
				else:
					exit()
		except Exception as error:
			print(error)
except Exception as error:
	print(error)
with open("authToken.txt", "w") as token:
    token.write(str(client.authToken))
clientMid = client.profile.mid
clientStart = time.time()
clientPoll = OEPoll(client)

languageOpen = codecs.open("language.json","r","utf-8")
readOpen = codecs.open("read.json","r","utf-8")
settingsOpen = codecs.open("setting.json","r","utf-8")
unsendOpen = codecs.open("unsend.json","r","utf-8")

language = json.load(languageOpen)
read = json.load(readOpen)
settings = json.load(settingsOpen)
unsend = json.load(unsendOpen)

def restartBot():
	print ("[ INFO ] BOT RESETTED")
	python = sys.executable
	os.execl(python, python, *sys.argv)

def logError(text):
    client.log("[ ERROR ] {}".format(str(text)))
    tz = pytz.timezone("Asia/Makassar")
    timeNow = datetime.now(tz=tz)
    timeHours = datetime.strftime(timeNow,"(%H:%M)")
    day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
    hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    inihari = datetime.now(tz=tz)
    hr = inihari.strftime('%A')
    bln = inihari.strftime('%m')
    for i in range(len(day)):
        if hr == day[i]: hasil = hari[i]
    for k in range(0, len(bulan)):
        if bln == str(k): bln = bulan[k-1]
    time = "{}, {} - {} - {} | {}".format(str(hasil), str(inihari.strftime('%d')), str(bln), str(inihari.strftime('%Y')), str(inihari.strftime('%H:%M:%S')))
    with open("errorLog.txt","a") as error:
        error.write("\n[{}] {}".format(str(time), text))

def timeChange(secs):
	mins, secs = divmod(secs,60)
	hours, mins = divmod(mins,60)
	days, hours = divmod(hours,24)
	weeks, days = divmod(days,7)
	months, weeks = divmod(weeks,4)
	text = ""
	if months != 0: text += "%02d月" % (months)
	if weeks != 0: text += "%02d週" % (weeks)
	if days != 0: text += "%02d 天" % (days)
	if hours !=  0: text += "%02d時" % (hours)
	if mins != 0: text += "%02d分" % (mins)
	if secs != 0: text += "%02d秒" % (secs)
	if text[0] == " ":
		text = text[1:]
	return text

def command(text):
	pesan = text.lower()
	if settings["setKey"] == True:
		if pesan.startswith(settings["keyCommand"]):
			cmd = pesan.replace(settings["keyCommand"],"")
		else:
			cmd = "Undefined command"
	else:
		cmd = text.lower()
	return cmd

def backupData():
	try:
		backup = read
		f = codecs.open('read.json','w','utf-8')
		json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
		backup = settings
		f = codecs.open('setting.json','w','utf-8')
		json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
		backup = unsend
		f = codecs.open('unsend.json','w','utf-8')
		json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
		return True
	except Exception as error:
		logError(error)
		return False

def clientBot(op):
	try:
		if op.type == 0:
			print ("[ 0 ] END OF OPERATION")
			return

		if op.type == 13:
			print ("[ 13 ] NOTIFIED INVITE INTO GROUP")
			if settings["autoJoin"] and clientMid in op.param3:
				client.acceptGroupInvitation(op.param1)
				client.sendMention(op.param1, settings["autoJoinMessage"], [op.param2])

		if op.type == 26:
			try:
				print("[ 25 ] SEND MESSAGE")
				msg = op.message
				text = str(msg.text)
				msg_id = msg.id
				receiver = msg.to
				sender = msg._from
				cmd = command(text)
				if msg.toType == 0 or msg.toType == 1 or msg.toType == 2:
					if msg.toType == 0:
						if sender != client.profile.mid:
							to = sender
						else:
							to = receiver
					elif msg.toType == 1:
						to = receiver
					elif msg.toType == 2:
						to = receiver
					if msg.contentType == 0:
                        try:
							unsendTime = time.time()
							unsend[msg_id] = {"text": text, "from": sender, "time": unsendTime}
						except Exception as error:
							logError(error)
                            
						if cmd == "logout":
							client.sendMessage(to, "關...關機")
							sys.exit("[ INFO ] BOT SHUTDOWN")
							return
						elif cmd.lower() == "restart":
							client.sendMessage(to, "我會回來的")
							restartBot()
						elif cmd.lower()=="speed":
							start = time.time()
							client.sendMessage(to, "測試測試")
							elapsed_time = time.time()-start
							client.sendMessage(to, "延遲{}秒".format(str(elapsed_time)))
						elif cmd.lower() == "runtime":
							timeNow = time.time()
							runtime = timeNow - clientStart
							runtime = timeChange(runtime)
							client.sendMessage(to, "已經開機{}".format(str(runtime)))
                            
                        elif cmd.lower().startswith("c"):
						    if cmd.lower().startswith("cname: "):
							    sep = text.split(" ")
							    name = text.replace(sep[0] + " ","")
							    if len(name) <= 20:
								    profile = client.getProfile()
								    profile.displayName = name
								    client.updateProfile(profile)
								    client.sendMessage(to, "我的名字是 {}打".format(name))
						    elif cmd.lower().startswith("cbio: "):
							    sep = text.split(" ")
							    bio = text.replace(sep[0] + " ","")
							    if len(bio) <= 500:
								    profile = client.getProfile()
								    profile.pictureStatus
								    profile.statusMessage = bio
								    client.updateProfile(profile)
								    client.sendMessage(to, "我的個簽是{}".format(bio))
                            elif cmd.startswith("cgpname: "):
								if msg.toType == 2:
									sep = text.split(" ")
									groupname = text.replace(sep[0] + " ","")
									if len(groupname) <= 20:
										group = client.getGroup(to)
										group.name = groupname
										client.updateGroup(group)
										client.sendMessage(to, "群組名稱是{}打".format(groupname))
                                        
						elif cmd.lower().startswith("m"):
                        	elif cmd.lower() == "me":
								client.sendMention(to, "@!", [sender])
								client.sendContact(to, sender)
							elif cmd.lower() == "mypf":
								contact, result = client.getContact(sender), "個人資料打: "
								myself = { "名字": "@!", "Mid":"{}".format(contact.mid), "個簽":"{}".format(contact.statusMessage) }
								pic, cover="http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus), client.getProfileCoverURL(sender)
								for i in myself.keys():
								    result += "\n=>"+i+": "+myself[i]
								client.sendMention(to, result, [sender])
								client.sendImageWithURL(to, pic)
								client.sendImageWithURL(to, cover)
							elif cmd == "mymid":
								contact = client.getContact(sender)
								client.sendMention(to, "@!: {}".format(contact.mid), [sender])
							elif cmd == "mypic":
								contact = client.getContact(sender)
								client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus))
							elif cmd == "myvdo":
								contact = client.getContact(sender)
								if contact.videoProfile == None:
									return client.sendMessage(to, "沒有影片的拉")
								client.sendVideoWithURL(to, "http://dl.profile.line-cdn.net/{}/vp".format(contact.pictureStatus))
							elif cmd == "mycov":
								cover = client.getProfileCoverURL(sender)
								client.sendImageWithURL(to, str(cover))
						
                        elif cmd.lower().startswith("g"):
                            elif cmd.lower().startswith("gmid "):
								if 'MENTION' in msg.contentMetadata.keys()!= None:
									names = re.findall(r'@(\w+)', text)
									mention = ast.literal_eval(msg.contentMetadata['MENTION'])
									mentionees = mention['MENTIONEES']
								    lists = []
								    for mention in mentionees:
									    if mention["M"] not in lists:
										    lists.append(mention["M"])
								    for ls in lists:
									    client.sendMention(to, "@!: {}".format(ls), [ls])
						    elif cmd.startswith("gbio "):
							    if 'MENTION' in msg.contentMetadata.keys()!= None:
								    names = re.findall(r'@(\w+)', text)
								    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								    mentionees = mention['MENTIONEES']
								    lists = []
								    for mention in mentionees:
									    if mention["M"] not in lists:
										    lists.append(mention["M"])
								    for ls in lists:
									    contact = client.getContact(ls)
									    client.sendMention(to, "@!: {}".format(contact.statusMessage), [ls])
						    elif cmd.startswith("gpic "):
							    if 'MENTION' in msg.contentMetadata.keys()!= None:
								    names = re.findall(r'@(\w+)', text)
								    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								    mentionees = mention['MENTIONEES']
								    lists = []
								    for mention in mentionees:
									    if mention["M"] not in lists:
										    lists.append(mention["M"])
								    for ls in lists:
									    contact = client.getContact(ls)
									    client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus))
						    elif cmd.startswith("gvdo "):
							    if 'MENTION' in msg.contentMetadata.keys()!= None:
							    	names = re.findall(r'@(\w+)', text)
								    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								    mentionees = mention['MENTIONEES']
								    lists = []
								    for mention in mentionees:
								    	if mention["M"] not in lists:
									    	lists.append(mention["M"])
								    for ls in lists:
									    contact = client.getContact(ls)
									    if contact.videoProfile == None:
									    	return client.sendMention(to, "@!不是影片的拉", [ls])
									    client.sendVideoWithURL(to, "http://dl.profile.line-cdn.net/{}/vp".format(contact.pictureStatus))
							elif cmd.startswith("gcov "):
								if 'MENTION' in msg.contentMetadata.keys()!= None:
									names = re.findall(r'@(\w+)', text)
									mention = ast.literal_eval(msg.contentMetadata['MENTION'])
									mentionees = mention['MENTIONEES']
									lists = []
									for mention in mentionees:
										if mention["M"] not in lists:
											lists.append(mention["M"])
									for ls in lists:
										cover = client.getProfileCoverURL(ls)
										client.sendImageWithURL(to, str(cover))
                                
                            elif cmd == "gpid":
								if msg.toType == 2:
									group = client.getGroup(to)
									client.sendMessage(to, "Group ID : {}".format(group.id))
                            elif cmd == "gppic":
								if msg.toType == 2:
									group = client.getGroup(to)
									groupPicture = "http://dl.profile.line-cdn.net/{}".format(group.pictureStatus)
									client.sendImageWithURL(to, groupPicture)
                        	elif cmd == "gpinfo":
								group = client.getGroup(to)
								try:
									try:
										groupCreator = group.creator.mid
									except:
										groupCreator = "從缺"
									if group.invitee is None:
										groupPending = "0"
									else:
										groupPending = str(len(group.invitee))
									if group.preventedJoinByTicket == True:
										groupQr = "Tertutup"
										groupTicket = "Tidak ada"
									else:
										groupQr = "Terbuka"
										groupTicket = "https://line.me/R/ti/g/{}".format(str(client.reissueGroupTicket(group.id)))
									ret_ = "╔══[ Group Information ]"
									ret_ += "\n╠ Nama Group : {}".format(group.name)
									ret_ += "\n╠ 群組ID : {}".format(group.id)
									ret_ += "\n╠ 革命者 : @!"
									ret_ += "\n╠ 成員 : {}".format(str(len(group.members)))
									ret_ += "\n╠ Jumlah Pending : {}".format(groupPending)
									ret_ += "\n╠ Group Qr : {}".format(groupQr)
									ret_ += "\n╠ Group Ticket : {}".format(groupTicket)
									ret_ += "\n╚══[ Success ]"
									client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(group.pictureStatus))
									client.sendMention(to, str(ret_), [groupCreator])
								except:
									ret_ = "╔══[ Group Information ]"
									ret_ += "\n╠ Nama Group : {}".format(group.name)
									ret_ += "\n╠ ID Group : {}".format(group.id)
									ret_ += "\n╠ Pembuat : {}".format(groupCreator)
									ret_ += "\n╠ Jumlah Member : {}".format(str(len(group.members)))
									ret_ += "\n╠ Jumlah Pending : {}".format(groupPending)
									ret_ += "\n╠ Group Qr : {}".format(groupQr)
									ret_ += "\n╠ Group Ticket : {}".format(groupTicket)
									ret_ += "\n╚══[ Success ]"
									client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(group.pictureStatus))
									client.sendMessage(to, str(ret_))
                            elif cmd.startswith("gpbroadcast: "):
								sep = text.split(" ")
								txt = text.replace(sep[0] + " ","")
								groups = client.getGroupIdsJoined()
								for group in groups:
									client.sendMessage(group, "{}".format(str(txt)))
								client.sendMessage(to, "以傳送給{}個群組".format(str(len(groups))))
								
                        elif cmd == "邀請名單":
							if msg.toType == 2:
								group = client.getGroup(to)
								ret_ = "╔══[ 邀請名單 ]"
								no = 0
								if group.invitee is None or group.invitee == []:
									return client.sendMessage(to, "沒有的拉")
								else:
									for pending in group.invitee:
										no += 1
										ret_ += "\n╠ {}. {}".format(str(no), str(pending.displayName))
									ret_ += "\n╚══[ 總共 {} 正在邀請 ]".format(str(len(group.invitee)))
									client.sendMessage(to, str(ret_)
                        elif cmd == "群組成員":
							if msg.toType == 2:
								group = client.getGroup(to)
								num = 0
								ret_ = "╔══[ 群組成員 ]"
								for contact in group.members:
									num += 1
									ret_ += "\n╠ {}. {}".format(num, contact.displayName)
								ret_ += "\n╚══[ 總共 {} 成員 ]".format(len(group.members))
								client.sendMessage(to, ret_)
                        
						elif cmd == "opqr":
							if msg.toType == 2:
								group = client.getGroup(to)
								group.preventedJoinByTicket = False
								client.updateGroup(group)
								groupUrl = client.reissueGroupTicket(to)
								client.sendMessage(to, "Berhasil membuka QR Group\n\nGroupURL : line://ti/g/{}".format(groupUrl))
						elif cmd == "csqr":
							if msg.toType == 2:
								group = client.getGroup(to)
								group.preventedJoinByTicket = True
								client.updateGroup(group)
								client.sendMessage(to, "Berhasil menutup QR Group")
                                    
						elif cmd == "@-@":
							tz = pytz.timezone("Asia/Makassar")
							timeNow = datetime.now(tz=tz)
							day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
							hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
							bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
							hr = timeNow.strftime("%A")
							bln = timeNow.strftime("%m")
							for i in range(len(day)):
								if hr == day[i]: hasil = hari[i]
							for k in range(0, len(bulan)):
								if bln == str(k): bln = bulan[k-1]
							readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nJam : [ " + timeNow.strftime('%H:%M:%S') + " ]"
							if to in read['readPoint']:
								try:
									del read['readPoint'][to]
									del read['readMember'][to]
								except:
									pass
								read['readPoint'][to] = msg_id
								read['readMember'][to] = []
								client.sendMessage(to, "靜悄悄")
							else:
								try:
									del read['readPoint'][to]
									del read['readMember'][to]
								except:
									pass
								read['readPoint'][to] = msg_id
								read['readMember'][to] = []
								client.sendMessage(to, "Set reading point : \n{}".format(readTime))
						elif cmd == "@-@x":
							tz = pytz.timezone("Asia/Makassar")
							timeNow = datetime.now(tz=tz)
							day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
							hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
							bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
							hr = timeNow.strftime("%A")
							bln = timeNow.strftime("%m")
							for i in range(len(day)):
								if hr == day[i]: hasil = hari[i]
							for k in range(0, len(bulan)):
								if bln == str(k): bln = bulan[k-1]
							readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nJam : [ " + timeNow.strftime('%H:%M:%S') + " ]"
							if to not in read['readPoint']:
								client.sendMessage(to,"Lurking telah dinonaktifkan")
							else:
								try:
									del read['readPoint'][to]
									del read['readMember'][to]
								except:
									pass
								client.sendMessage(to, "Delete reading point : \n{}".format(readTime))
						elif cmd == "@-@!":
							if to in read['readPoint']:
								if read["readMember"][to] == []:
									return client.sendMessage(to, "Tidak Ada Sider")
								else:
									no = 0
									result = "╔══[ Reader ]"
									for dataRead in read["readMember"][to]:
										no += 1
										result += "\n╠ {}. @!".format(str(no))
									result += "\n╚══[ Total {} Sider ]".format(str(len(read["readMember"][to])))
									client.sendMention(to, result, read["readMember"][to])
									read['readMember'][to] = []
						if text is None: return
			except Exception as error:
				logError(error)


		if op.type == 55:
			print ("[ 55 ] NOTIFIED READ MESSAGE")
			if op.param1 in read["readPoint"]:
				if op.param2 not in read["readMember"][op.param1]:
					read["readMember"][op.param1].append(op.param2)


		if op.type == 65:
			try:
					to = op.param1
					sender = op.param2
					if sender in unsend:
						unsendTime = time.time()
						contact = client.getContact(unsend[sender]["from"])
						if "text" in unsend[sender]:
							try:
								sendTime = unsendTime - unsend[sender]["time"]
								sendTime = timeChange(sendTime)
								ret_ = "收回的訊息: "
								ret_ += "\n=> 傳送人 : @!"
								ret_ += "\n=> 收回時間 : {} 前".format(sendTime)
								ret_ += "\n=> 訊息 : {}".format(unsend[sender]["text"])
								client.sendMention(to, ret_, [contact.mid])
								del unsend[sender]
							except:
								del unsend[sender]
					else:
						client.sendMessage(to, "我聞到了收回仔的味道;(((")
			except Exception as error:
				logError(error)
		backupData()
	except Exception as error:
		logError(error)

def run():
	while True:
		ops = clientPoll.singleTrace(count=50)
		if ops != None:
			for op in ops:
				try:
					clientBot(op)
				except Exception as error:
					logError(error)
				clientPoll.setRevision(op.revision)

if __name__ == "__main__":
	run()

