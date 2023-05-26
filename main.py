import base64
import customtkinter
import openai
import os.path

from tkinter.filedialog import askdirectory
from csv_writer import write_csv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
openai.api_key = "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"
clientID = "244784056237-h1hfrhgtp8c2n6gj61hs673naat6bfcm.apps.googleusercontent.com"

filepath = ""
emailID = ""
service = ""

root = customtkinter.CTk()
root.geometry("380x420")
root.title("Sentiment Analyser")


def UpdateLabelFinish () :
	label.configure(text = "Completed!")

def UpdateLabelWait () :
	label.configure(text = "Please Wait...")

def SaveFile (customer, analysisDetails) :
	filename = askdirectory()
	write_csv(customer, analysisDetails, filename)
	UpdateLabelFinish()
	return filename

def analyseSentiment (text) :

	if len(text) > 4096:
		text = text[:4096]

	response = openai.Completion.create(
		model="text-davinci-003",
		prompt=f"Decide whether this text's sentiment is highly positive, mildly positive, neutral, mildly negative, or highly negative.\n\nText: \"[{text}\"\nSentiment:",
		temperature=0.1,
		max_tokens=60,
		frequency_penalty=0.5,
		)
	
	return response["choices"][0]["text"]

def data_encoder(text):
	if len(text)>0:
		message = base64.urlsafe_b64decode(text)
		message = str(message, 'utf-8')
	return message

def readMessage(content)->str:
	message = None
	if "data" in content['payload']['body']:
		message = content['payload']['body']['data']
		message = data_encoder(message)
	elif "data" in content['payload']['parts'][0]['body']:
		message = content['payload']['parts'][0]['body']['data']
		message = data_encoder(message)
	else:
		message = "This message is neutral!"
		print("body has no data.")
	return analyseSentiment(message)

def getMails (service) :

	UpdateLabelWait()

	emailID = emailEntry.get()
	customer = emailID.split("@")
	customer = str(customer[0])
	mails = service.users().messages().list(userId = "me", maxResults = 500).execute()

	analysisDetails = []

	for messageDetail in mails['messages']:
		mailID = messageDetail['id']
		messages = service.users().messages().get(userId = 'me', id = mailID, format = "full").execute()
		headers = messages['payload']['headers']

		for d in headers:
			if d['name'] == 'From':
				sender = d['value']

		sender = sender.split("<"); sender = sender[-1].split(">"); sender = str(sender[0])
		if (emailID == sender):

			headers = messages['payload']['headers']
			for d in headers:
				if d['name'] == 'Subject':
					subject = d['value']
				if d['name'] == 'Date':
					date = d['value']
				if d['name'] == 'From':
					sender = d['value']

			analysis = readMessage(messages)
			analysisDetails.append([str(date), str(subject), str(analysis)])
	SaveFile(customer, analysisDetails)

def main():
	global service
	creds = None
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		with open('token.json', 'w') as token:
			token.write(creds.to_json())
	try:
		service = build('gmail', 'v1', credentials=creds)
	except HttpError as error:
		print(f'An error occurred: {error}')

frame = customtkinter.CTkFrame(master = root)
frame.pack(pady = 20, padx = 60, fill = "both", expand = True)

label = customtkinter.CTkLabel(master = frame, text = "SentimentAnalyser")
label.pack(pady = 12, padx = 10)

emailEntry = customtkinter.CTkEntry(master = frame, placeholder_text = "email@email.com",
				    width = 240, textvariable = emailID)
emailEntry.pack(padx=20, pady=10)

saveButton = customtkinter.CTkButton(master = frame, text = "Calculate Sentiment", command = lambda: getMails(service))
saveButton.pack(pady = 12, padx = 10)

savedLabel = customtkinter.CTkLabel(master = frame, text = "...")
savedLabel.pack(pady = 12, padx = 10)

def exitProgram():
	global root
	root.destroy()
	quit()

quitButton = customtkinter.CTkButton(master = frame, text = "Quit", command = exitProgram)
quitButton.pack(pady = 12, padx = 10)

if __name__ == '__main__':
	main()

root.mainloop()

