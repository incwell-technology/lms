import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials


def fcm(fcm, data, reason):
    if (not len(firebase_admin._apps)):
        cred = credentials.Certificate('mobile_api/ServiceAccountKey.json')
        default_app = firebase_admin.initialize_app(cred)

    if reason == "holiday": 
        message = messaging.Message(
            android=messaging.AndroidConfig(
                priority='normal',
                notification=messaging.AndroidNotification(
                    title='Holiday Notice',
                    body= "Today is holiday for " + data
                ),
            ),
            topic = reason,
        )
    if reason == "leave_apply": 
        title='Leave Request'
        body= data.user.first_name + " " + data.user.last_name +" has applied for leave"
    if reason == "reject_leave": 
        title='Leave Rejected'
        body= "Your leave has been rejected by " + data
    if reason == "approve_leave": 
        title='Leave Approved'
        body= "Your leave has been approved by " + data
    if reason == "compensation_apply": 
        title='Compensation Leave Request'
        body= data.user.first_name + " " + data.user.last_name +" has applied for compensation leave"
    if reason == "reject_compensation":    
        title='Compensation Leave Rejected'
        body= "Your compensation leave has been rejected by " + data
    if reason == "approve_compensation":      
        title='Compensation Leave Approved'
        body= "Your compensation leave has been approved by " + data
                
    if reason == "holiday": 
        message = messaging.Message(
            android=messaging.AndroidConfig(
                priority='normal',
                notification=messaging.AndroidNotification(
                    title='Holiday Notice',
                    body= "Today is holiday for " + data
                ),
            ),
            topic = reason,
        )
    if not reason == "holiday":
        message = messaging.Message(
            android=messaging.AndroidConfig(
                priority='normal',
                notification=messaging.AndroidNotification(
                    title= title,
                    body= body
                ),
            ),
            token = fcm,
        )
    response = messaging.send(message)
    print('Successfully sent message:', response)


def subcription(token,topic):
    if (not len(firebase_admin._apps)):
        cred = credentials.Certificate('mobile_api/ServiceAccountKey.json')
        default_app = firebase_admin.initialize_app(cred)
    
    registration_tokens = [
        token
    ]
    response = messaging.subscribe_to_topic(registration_tokens, topic)
    print(response.success_count, 'tokens were subscribed successfully to ' + topic)    
