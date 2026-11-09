// DivAlarm site header: mobile menu and account links. Loaded as the last module on
// every page, so it reuses the Firebase app a page has already started.
const top = document.getElementById("da-top");
const menuBtn = top ? top.querySelector(".da-menu") : null;

function setMenu(open) {
  if (!top || !menuBtn) return;
  top.classList.toggle("is-open", open);
  menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
}

if (menuBtn) {
  menuBtn.addEventListener("click", () => setMenu(!top.classList.contains("is-open")));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && top.classList.contains("is-open")) {
      setMenu(false);
      menuBtn.focus();
    }
  });
  top.querySelectorAll(".da-nav a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
}

const FIREBASE_CONFIG = {
  apiKey: "AIzaSyDB0uVFhbk3_2uEoCt8iz0LhE_2OOK_adQ",
  authDomain: "divergence-alarm.firebaseapp.com",
  projectId: "divergence-alarm",
  storageBucket: "divergence-alarm.firebasestorage.app",
  messagingSenderId: "912910128238",
  appId: "1:912910128238:web:a42ca6881960fcde76427f",
  measurementId: "G-NGCZKMQF67",
};

async function wireAccount() {
  const signIn = document.getElementById("da-signin");
  const account = document.getElementById("da-account");
  const signOutBtn = document.getElementById("da-signout");
  if (!signIn || !account || !signOutBtn) return;
  try {
    const [{ initializeApp, getApps, getApp }, { getAuth, onAuthStateChanged, signOut }] = await Promise.all([
      import("https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js"),
      import("https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js"),
    ]);
    const app = getApps().length ? getApp() : initializeApp(FIREBASE_CONFIG);
    const auth = getAuth(app);
    onAuthStateChanged(auth, (user) => {
      signIn.hidden = !!user;
      account.hidden = !user;
      signOutBtn.hidden = !user;
    });
    signOutBtn.addEventListener("click", async () => {
      try {
        await signOut(auth);
        localStorage.clear();
        location.href = "index.html";
      } catch (e) {
        console.error("Sign-out failed", e);
      }
    });
  } catch (e) {
    // Offline or blocked CDN: keep the plain "Sign in" link.
    console.warn("Account links unavailable", e);
  }
}

wireAccount();
