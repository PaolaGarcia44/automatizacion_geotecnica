import { initializeApp, getApps, FirebaseApp } from 'firebase/app'
import type { Auth } from 'firebase/auth'
import type { Firestore } from 'firebase/firestore'
import type { FirebaseStorage } from 'firebase/storage'

let app: FirebaseApp | undefined
let auth: Auth | undefined
let firestore: Firestore | undefined
let storage: FirebaseStorage | undefined

// Initialize Firebase only if environment variables are available
const initializeFirebase = () => {
  // Check if Firebase is already initialized
  if (getApps().length > 0) {
    return getApps()[0]
  }

  const requiredEnvVars = [
    'NEXT_PUBLIC_FIREBASE_API_KEY',
    'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
    'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
    'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
    'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
    'NEXT_PUBLIC_FIREBASE_APP_ID',
  ]

  const missingVars = requiredEnvVars.filter((varName) => !process.env[varName])

  if (missingVars.length > 0) {
    console.warn(
      `Firebase is not fully configured. Missing environment variables: ${missingVars.join(', ')}. 
      Please copy .env.local.example to .env.local and fill in your Firebase credentials.`
    )
    return null
  }

  const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  }

  try {
    app = initializeApp(firebaseConfig)
    return app
  } catch (error) {
    console.error('Failed to initialize Firebase:', error)
    return null
  }
}

// Lazy load Firebase modules
export const getFirebaseApp = (): FirebaseApp | null => {
  if (app === undefined) {
    return initializeFirebase()
  }
  return app
}

export const getFirebaseAuth = (): Auth | null => {
  const firebaseApp = getFirebaseApp()
  if (!firebaseApp) return null

  if (auth === undefined) {
    try {
      const { getAuth } = require('firebase/auth')
      auth = getAuth(firebaseApp)
    } catch (error) {
      console.error('Failed to initialize Firebase Auth:', error)
      auth = null as unknown as Auth
    }
  }
  return auth || null
}

export const getFirebaseFirestore = (): Firestore | null => {
  const firebaseApp = getFirebaseApp()
  if (!firebaseApp) return null

  if (firestore === undefined) {
    try {
      const { getFirestore } = require('firebase/firestore')
      firestore = getFirestore(firebaseApp)
    } catch (error) {
      console.error('Failed to initialize Firebase Firestore:', error)
      firestore = null as unknown as Firestore
    }
  }
  return firestore || null
}

export const getFirebaseStorage = (): FirebaseStorage | null => {
  const firebaseApp = getFirebaseApp()
  if (!firebaseApp) return null

  if (storage === undefined) {
    try {
      const { getStorage } = require('firebase/storage')
      storage = getStorage(firebaseApp)
    } catch (error) {
      console.error('Failed to initialize Firebase Storage:', error)
      storage = null as unknown as FirebaseStorage
    }
  }
  return storage || null
}

export { app }
