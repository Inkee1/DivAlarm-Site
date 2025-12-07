// TV Webhook Authentication Module
import { initializeApp, getApps, getApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { 
  getAuth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  sendEmailVerification,
  sendPasswordResetEmail,
  GoogleAuthProvider, 
  signInWithPopup,
  fetchSignInMethodsForEmail
} from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js";

// Firebase Config
const firebaseConfig = {
  apiKey: "AIzaSyDB0uVFhbk3_2uEoCt8iz0LhE_2OOK_adQ",
  authDomain: "divergence-alarm.firebaseapp.com",
  projectId: "divergence-alarm",
  storageBucket: "divergence-alarm.firebasestorage.app",
  messagingSenderId: "912910128238",
  appId: "1:912910128238:web:a42ca6881960fcde76427f",
  measurementId: "G-NGCZKMQF67"
};

// Initialize Firebase
const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

window.app = app;
window.auth = auth;

// Helper: Create user document in Firestore
async function maybeCreateUser(user) {
  if (!user) return;
  const userRef = doc(db, "users", user.uid);
  const userSnap = await getDoc(userRef);
  
  if (userSnap.exists()) {
    console.log("✅ User document already exists:", user.uid);
    return;
  }
  
  const userData = {
    email: user.email || "",
    uid: user.uid,
    createdTime: new Date(),
  };
  
  await setDoc(userRef, userData);
  console.log("✅ Created user document:", user.uid);
}

// Helper: Fetch user membership data
async function fetchUserMembershipData(user) {
  if (!user) return;
  
  await user.reload();
  const isEmailVerified = user.emailVerified;
  localStorage.setItem("isEmailVerified", isEmailVerified);
  
  const userRef = doc(db, "users", user.uid);
  
  try {
    const userSnap = await getDoc(userRef);
    if (userSnap.exists()) {
      const userData = userSnap.data();
      localStorage.setItem("useremail", userData.email);
      localStorage.setItem("membership", userData.membership);
      localStorage.setItem("expired", userData.expired?.seconds);
      localStorage.setItem("isCanceled", userData.isCanceled);
      localStorage.setItem("wallet", userData.wallet);
      return userData;
    }
  } catch (err) {
    console.error("🔥 Failed to fetch user data:", err);
  }
}

// Helper: Check ban status
async function checkBanStatus(email) {
  try {
    const banCheckRes = await fetch(
      `https://asia-northeast1-divergence-alarm.cloudfunctions.net/sendReferralNotification/check_ban/${encodeURIComponent(email)}`
    );
    const banData = await banCheckRes.json();
    return banData.banned;
  } catch (err) {
    console.error("❌ Failed to check ban status:", err);
    return false;
  }
}

// Helper: Show error message
function showError(form, message) {
  // Remove existing error
  const existingError = form.querySelector('.error-message');
  if (existingError) existingError.remove();
  
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.textContent = message;
  form.insertBefore(errorDiv, form.firstChild);
}

// Helper: Clear error message
function clearError(form) {
  const existingError = form.querySelector('.error-message');
  if (existingError) existingError.remove();
}

// ========== SIGN IN ==========
const signinForm = document.getElementById('signin-form');
const googleSigninBtn = document.getElementById('google-signin-btn');

if (signinForm) {
  signinForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError(signinForm);
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const submitBtn = document.getElementById('signin-btn');
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Signing in...</span>';
    
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      if (!user.emailVerified) {
        showError(signinForm, "🚫 Please verify your email before logging in. Check your inbox for the verification link.");
        await auth.signOut();
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>Sign In</span><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        return;
      }
      
      const idToken = await user.getIdToken();
      localStorage.setItem("idToken", idToken);
      
      await maybeCreateUser(user);
      await fetchUserMembershipData(user);
      
      alert("Login successful!");
      window.location.href = "index.html";
      
    } catch (error) {
      console.error("❌ Login error:", error);
      let errorMessage = "Login failed. Please check your credentials.";
      
      if (error.code === 'auth/user-not-found') {
        errorMessage = "No account found with this email.";
      } else if (error.code === 'auth/wrong-password') {
        errorMessage = "Incorrect password.";
      } else if (error.code === 'auth/invalid-email') {
        errorMessage = "Invalid email address.";
      } else if (error.code === 'auth/too-many-requests') {
        errorMessage = "Too many failed attempts. Please try again later.";
      }
      
      showError(signinForm, errorMessage);
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Sign In</span><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }
  });
}

if (googleSigninBtn) {
  googleSigninBtn.addEventListener('click', async () => {
    const provider = new GoogleAuthProvider();
    
    try {
      const userCredential = await signInWithPopup(auth, provider);
      const user = userCredential.user;
      
      // Check ban status
      const isBanned = await checkBanStatus(user.email);
      if (isBanned) {
        alert("🚫 This email was recently used to delete an account. You can sign up again after 7 days.");
        await auth.signOut();
        return;
      }
      
      const idToken = await user.getIdToken();
      localStorage.setItem("idToken", idToken);
      
      await maybeCreateUser(user);
      await fetchUserMembershipData(user);
      
      alert("Google Login successful!");
      window.location.href = "index.html";
      
    } catch (error) {
      console.error("❌ Google Login error:", error);
      if (error.code !== 'auth/popup-closed-by-user') {
        alert("Google sign-in failed: " + error.message);
      }
    }
  });
}

// ========== SIGN UP ==========
const signupForm = document.getElementById('signup-form');
const googleSignupBtn = document.getElementById('google-signup-btn');

if (signupForm) {
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError(signupForm);
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const submitBtn = document.getElementById('signup-btn');
    
    // Validate passwords match
    if (password !== confirmPassword) {
      showError(signupForm, "🚫 Passwords do not match.");
      return;
    }
    
    // Validate password length
    if (password.length < 6) {
      showError(signupForm, "🚫 Password must be at least 6 characters.");
      return;
    }
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Creating account...</span>';
    
    try {
      // Check ban status
      const isBanned = await checkBanStatus(email);
      if (isBanned) {
        showError(signupForm, "🚫 This email was recently used to delete an account. You can sign up again after 7 days.");
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>Create Account</span><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        return;
      }
      
      // Check if email already exists
      const signInMethods = await fetchSignInMethodsForEmail(auth, email);
      if (signInMethods.length > 0) {
        showError(signupForm, "This email is already registered. Please sign in.");
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>Create Account</span><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        return;
      }
      
      // Create user
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Send verification email
      await sendEmailVerification(user);
      
      alert("Sign-up successful! Please check your email to verify your account.");
      window.location.href = "sign-in.html";
      
    } catch (error) {
      console.error("❌ Sign-up error:", error);
      let errorMessage = "Sign-up failed. Please try again.";
      
      if (error.code === 'auth/email-already-in-use') {
        errorMessage = "An account with this email already exists.";
      } else if (error.code === 'auth/invalid-email') {
        errorMessage = "Invalid email address.";
      } else if (error.code === 'auth/weak-password') {
        errorMessage = "Password is too weak. Please use at least 6 characters.";
      }
      
      showError(signupForm, errorMessage);
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Create Account</span><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }
  });
}

if (googleSignupBtn) {
  googleSignupBtn.addEventListener('click', async () => {
    const provider = new GoogleAuthProvider();
    
    try {
      const userCredential = await signInWithPopup(auth, provider);
      const user = userCredential.user;
      
      // Check ban status
      const isBanned = await checkBanStatus(user.email);
      if (isBanned) {
        alert("🚫 This email was recently used to delete an account. You can sign up again after 7 days.");
        await auth.signOut();
        return;
      }
      
      const idToken = await user.getIdToken();
      localStorage.setItem("idToken", idToken);
      
      await maybeCreateUser(user);
      await fetchUserMembershipData(user);
      
      alert("Google Sign-up successful!");
      window.location.href = "index.html";
      
    } catch (error) {
      console.error("❌ Google Sign-up error:", error);
      if (error.code !== 'auth/popup-closed-by-user') {
        alert("Google sign-up failed: " + error.message);
      }
    }
  });
}

// ========== FORGOT PASSWORD ==========
const forgotForm = document.getElementById('forgot-form');

if (forgotForm) {
  forgotForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError(forgotForm);
    
    const email = document.getElementById('email').value;
    const submitBtn = document.getElementById('reset-btn');
    const successMessage = document.getElementById('success-message');
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Sending...</span>';
    
    try {
      await sendPasswordResetEmail(auth, email);
      
      // Hide form and show success
      forgotForm.style.display = 'none';
      successMessage.style.display = 'flex';
      
    } catch (error) {
      console.error("❌ Password reset error:", error);
      let errorMessage = "Failed to send reset email. Please try again.";
      
      if (error.code === 'auth/user-not-found') {
        errorMessage = "No account found with this email.";
      } else if (error.code === 'auth/invalid-email') {
        errorMessage = "Invalid email address.";
      }
      
      showError(forgotForm, errorMessage);
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Send Reset Link</span><svg viewBox="0 0 24 24" fill="none"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }
  });
}

// ========== Mobile Menu Toggle ==========
document.addEventListener("DOMContentLoaded", () => {
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const mobileMenu = document.querySelector('.mobile-menu');
  
  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenuBtn.classList.toggle('active');
      mobileMenu.classList.toggle('active');
      document.body.classList.toggle('menu-open');
    });

    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenuBtn.classList.remove('active');
        mobileMenu.classList.remove('active');
        document.body.classList.remove('menu-open');
      });
    });
  }
});

