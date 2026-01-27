# Firebase Setup Instructions for Alertix

## Prerequisites
- Flutter SDK installed (version 3.x or higher)
- Firebase CLI installed (`npm install -g firebase-tools`)
- A Google account

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name: "Alertix" or your preferred name
4. Enable/disable Google Analytics as needed
5. Click "Create project"

## Step 2: Add Android App

1. In Firebase Console, click "Add app" and select Android
2. Enter package name: `com.alertix.app`
3. Enter app nickname: "Alertix Android"
4. Download `google-services.json`
5. Place it in: `android/app/google-services.json`

## Step 3: Add iOS App

1. In Firebase Console, click "Add app" and select iOS
2. Enter bundle ID: `com.alertix.app`
3. Enter app nickname: "Alertix iOS"
4. Download `GoogleService-Info.plist`
5. Place it in: `ios/Runner/GoogleService-Info.plist`

## Step 4: Enable Authentication

1. In Firebase Console, go to "Authentication"
2. Click "Get started"
3. Enable "Email/Password" provider
4. Optionally enable "Email link" for passwordless login

## Step 5: Set up Cloud Messaging (FCM)

### For Android:
1. The configuration is already set up via `google-services.json`
2. No additional setup required

### For iOS:
1. Go to Firebase Console > Project Settings > Cloud Messaging
2. Upload your APNs authentication key or certificates
3. In Xcode, enable "Push Notifications" capability
4. Enable "Background Modes" and check "Remote notifications"

## Step 6: Firebase Configuration in Flutter

Run the FlutterFire CLI to auto-configure:

```bash
# Install FlutterFire CLI
dart pub global activate flutterfire_cli

# Configure Firebase for your project
flutterfire configure --project=YOUR_PROJECT_ID
```

This will generate `lib/firebase_options.dart`

## Step 7: Update main.dart

Add Firebase initialization in `main.dart`:

```dart
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // ... rest of initialization
}
```

## Step 8: Test Push Notifications

### Using Firebase Console:
1. Go to Firebase Console > Cloud Messaging
2. Click "Send your first message"
3. Enter notification title and body
4. Target your app
5. Send the message

### Using REST API:
```bash
curl -X POST \
  https://fcm.googleapis.com/fcm/send \
  -H 'Authorization: key=YOUR_SERVER_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "to": "DEVICE_FCM_TOKEN",
    "notification": {
      "title": "Theft Detected!",
      "body": "Suspicious activity detected in monitored area"
    },
    "data": {
      "type": "theft_alert",
      "alert_id": "12345"
    }
  }'
```

## Troubleshooting

### Android Issues:
- Ensure `google-services.json` is in the correct location
- Check that the package name matches exactly
- Run `flutter clean` and rebuild

### iOS Issues:
- Ensure `GoogleService-Info.plist` is added to Xcode
- Check that bundle ID matches exactly
- Verify APNs certificates are properly configured
- Test on a real device (notifications don't work on simulators)

### General Issues:
- Check Firebase Console for any error messages
- Verify internet connectivity
- Check that all Firebase packages are properly installed

## Security Rules

### Firestore Rules (if using Firestore):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /alerts/{alertId} {
      allow read: if request.auth != null;
      allow write: if false; // Only backend can write
    }
  }
}
```

## Backend Integration

Your Raspberry Pi backend should send FCM notifications when theft is detected:

```python
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase Admin SDK
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

def send_theft_alert(device_token, alert_data):
    message = messaging.Message(
        notification=messaging.Notification(
            title='🚨 Theft Detected!',
            body='Suspicious activity detected in monitored area',
        ),
        data={
            'type': 'theft_alert',
            'alert_id': alert_data['id'],
            'image_url': alert_data['image_url'],
        },
        token=device_token,
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                channel_id='theft_alerts',
                priority='max',
            ),
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title='🚨 Theft Detected!',
                        body='Suspicious activity detected',
                    ),
                    sound='default',
                    badge=1,
                ),
            ),
        ),
    )

    response = messaging.send(message)
    print(f'Successfully sent message: {response}')
```

## Next Steps

1. Complete Firebase setup for both platforms
2. Test authentication flow
3. Configure backend to send FCM notifications
4. Set up proper security rules
5. Test end-to-end notification flow
