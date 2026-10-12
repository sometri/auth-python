from flask import request, session

SUPPORTED = ("en", "km")

TRANSLATIONS = {
    "en": {
        "auth": {
            "title": "Sign in to your account",
            "subtitle": "Welcome back to V1 Travel",
            "email": "Email address",
            "password": "Password",
            "forgotPassword": "Forgot password?",
            "loginButton": "Sign In",
            "loggingIn": "Signing in...",
            "noAccount": "Don't have an account?",
            "registerLink": "Create one",
            "invalidCredentials": "Invalid email or password.",
            "networkError": "Cannot connect to server. Please try again.",
            "loginFailed": "Login failed. Please try again.",
            "createAccount": "Create your account",
            "registerSubtitle": "Fill in the details to create your new account",
            "fullName": "Full name",
            "confirmPassword": "Confirm password",
            "register": "Sign Up",
            "creatingAccount": "Creating Account...",
            "registerSuccess": "Registration successful!",
            "redirectingToLogin": "Redirecting to login...",
            "registrationFailed": "Registration failed. Please try again.",
            "alreadyHaveAccount": "Already have an account?",
            "signIn": "Sign in",
            "success": "Success!",
            "redirecting": "Redirecting...",
            "forgotPasswordSubtitle": "Enter your email to receive a password reset link",
            "sendResetLink": "Send Reset Link",
            "sendingLink": "Sending link...",
            "sentSuccessfully": "Sent successfully!",
            "checkInbox": "Please check your inbox (and spam folder).",
            "resetNewPassword": "Set a new password",
            "newPasswordSubtitle": "Enter your new password below",
            "newPassword": "New password",
            "passwordMinLength": "Password must be at least 6 characters.",
            "passwordMinLengthShort": "At least 6 characters",
            "saveNewPassword": "Save New Password",
            "saving": "Saving...",
            "passwordResetSuccess": "Password Reset Successful!",
            "passwordChanged": "Your password has been changed successfully.",
            "clickHere": "Click here to log in",
            "invalidLink": "Invalid Link",
            "requestNewLink": "Request a new link",
            "twoFactorTitle": "Two-Factor Verification",
            "twoFactorSubtitle": "Enter the 6-digit code from your authenticator app",
            "twoFactorCode": "Verification code",
            "recoveryCodeNote": "You can also use one of your recovery codes (single use).",
            "verifyButton": "Verify",
            "verifying": "Verifying...",
            "backToLogin": "Back to login",
            "back": "Back",
            "logout": "Log out",
            "dashboardTitle": "You are signed in",
            "dashboardSubtitle": "This is the protected area of the V1 Travel auth demo.",
            "twoFactorSettings": "Two-Factor Authentication",
            "enable2fa": "Enable 2FA",
            "disable2fa": "Disable 2FA",
            "scanHint": "Add this secret to your authenticator app, then confirm a code.",
            "recoveryCodes": "Recovery codes",
            "twoFactorOn": "2FA enabled",
            "twoFactorOff": "2FA disabled",
            "twoFactorEnabledMsg": "Two-factor authentication enabled.",
            "twoFactorDisabledMsg": "Two-factor authentication disabled.",
            "resetLinkSent": "Password reset link has been sent to your email. (Dev: check the server console for the link.)",
            "errors": {
                "passwordsDontMatch": "Passwords do not match.",
                "passwordTooShort": "Password must be at least 6 characters.",
                "invalidResetLink": "Invalid reset link. Please request a new one.",
                "emailRequired": "Please enter your email address.",
                "invalid2fa": "Invalid or expired 2FA code.",
                "emailInUse": "That email is already registered.",
                "enterCode": "Enter the 6-digit code or a recovery code.",
                "fillAllFields": "Please fill in all fields.",
                "tooManyAttempts": "Too many attempts. Please wait a moment and try again.",
            },
        }
    },
    "km": {
        "auth": {
            "title": "ចូលគណនីរបស់អ្នក",
            "subtitle": "សូមស្វាគមន៍មកកាន់ V1 Travel",
            "email": "អ៊ីមែល",
            "password": "ពាក្យសម្ងាត់",
            "forgotPassword": "ភ្លេចពាក្យសម្ងាត់?",
            "loginButton": "ចូលគណនី",
            "loggingIn": "កំពុងចូល...",
            "noAccount": "មិនទាន់មានគណនី?",
            "registerLink": "បង្កើតគណនី",
            "invalidCredentials": "អ៊ីមែល ឬលេខសម្ងាត់មិនត្រឹមត្រូវ។",
            "networkError": "មិនអាចភ្ជាប់ទៅ Server បានទេ។",
            "loginFailed": "ការចូលគណនីមិនបានសម្រេច។",
            "createAccount": "បង្កើតគណនីរបស់អ្នក",
            "registerSubtitle": "សូមបំពេញព័ត៌មានដើម្បីបង្កើតគណនីថ្មី",
            "fullName": "ឈ្មោះពេញ",
            "confirmPassword": "បញ្ជាក់ពាក្យសម្ងាត់",
            "register": "ចុះឈ្មោះ",
            "creatingAccount": "កំពុងបង្កើតគណនី...",
            "registerSuccess": "ការចុះឈ្មោះជោគជ័យ!",
            "redirectingToLogin": "កំពុងនាំទៅទំព័រចូលគណនី...",
            "registrationFailed": "ការចុះឈ្មោះមិនបានសម្រេច។",
            "alreadyHaveAccount": "មានគណនីរួចហើយ?",
            "signIn": "ចូលគណនី",
            "success": "ជោគជ័យ!",
            "redirecting": "កំពុងនាំទៅ...",
            "forgotPasswordSubtitle": "បញ្ចូលអ៊ីមែលដើម្បីទទួលតំណកំណត់ពាក្យសម្ងាត់",
            "sendResetLink": "ផ្ញើតំណកំណត់",
            "sendingLink": "កំពុងផ្ញើតំណ...",
            "sentSuccessfully": "ផ្ញើបានជោគជ័យ!",
            "checkInbox": "សូមពិនិត្យប្រអប់សារ (និងថត Spam)។",
            "resetNewPassword": "កំណត់ពាក្យសម្ងាត់ថ្មី",
            "newPasswordSubtitle": "បញ្ចូលពាក្យសម្ងាត់ថ្មីរបស់អ្នក",
            "newPassword": "ពាក្យសម្ងាត់ថ្មី",
            "passwordMinLength": "ពាក្យសម្ងាត់ត្រូវមានយ៉ាងតិច ៦ តួអក្សរ។",
            "passwordMinLengthShort": "យ៉ាងតិច ៦ តួអក្សរ",
            "saveNewPassword": "រក្សាទុកពាក្យសម្ងាត់ថ្មី",
            "saving": "កំពុងរក្សាទុក...",
            "passwordResetSuccess": "កំណត់ពាក្យសម្ងាត់ជោគជ័យ!",
            "passwordChanged": "ពាក្យសម្ងាត់របស់អ្នកបានប្តូរជោគជ័យ។",
            "clickHere": "ចុចទីនេះដើម្បីចូលគណនី",
            "invalidLink": "តំណមិនត្រឹមត្រូវ",
            "requestNewLink": "ស្នើសុំតំណថ្មី",
            "twoFactorTitle": "ការផ្ទៀងផ្ទាត់ពីរជំហាន",
            "twoFactorSubtitle": "បញ្ចូលលេខកូដ ៦ តួពីកម្មវិធី Authenticator",
            "twoFactorCode": "លេខកូដផ្ទៀងផ្ទាត់",
            "recoveryCodeNote": "អ្នកអាចប្រើ recovery code មួយ (ប្រើបានតែម្តង)។",
            "verifyButton": "ផ្ទៀងផ្ទាត់",
            "verifying": "កំពុងផ្ទៀងផ្ទាត់...",
            "backToLogin": "ត្រឡប់ទៅចូលគណនី",
            "back": "ត្រឡប់",
            "logout": "ចាកចេញ",
            "dashboardTitle": "អ្នកបានចូលគណនីរួចហើយ",
            "dashboardSubtitle": "នេះជាតំបន់ការពារនៃគម្រូ V1 Travel។",
            "twoFactorSettings": "ការផ្ទៀងផ្ទាត់ពីរជំហាន",
            "enable2fa": "បើក 2FA",
            "disable2fa": "បិទ 2FA",
            "scanHint": "បន្ថែម secret នេះទៅកម្មវិធី Authenticator រួចបញ្ជាក់លេខកូដ។",
            "recoveryCodes": "Recovery codes",
            "twoFactorOn": "បើក 2FA",
            "twoFactorOff": "បិទ 2FA",
            "twoFactorEnabledMsg": "បានបើកការផ្ទៀងផ្ទាត់ពីរជំហាន។",
            "twoFactorDisabledMsg": "បានបិទការផ្ទៀងផ្ទាត់ពីរជំហាន។",
            "resetLinkSent": "តំណកំណត់ពាក្យសម្ងាត់ត្រូវបានផ្ញើទៅអ៊ីមែលរបស់អ្នកហើយ។",
            "errors": {
                "passwordsDontMatch": "ពាក្យសម្ងាត់មិនដូចគ្នាទេ។",
                "passwordTooShort": "ពាក្យសម្ងាត់ត្រូវមានយ៉ាងតិច ៦ តួអក្សរ។",
                "invalidResetLink": "តំណមិនត្រឹមត្រូវ។ សូមស្នើសុំតំណថ្មី។",
                "emailRequired": "សូមបញ្ចូលអ៊ីមែលរបស់អ្នក។",
                "invalid2fa": "លេខកូដ 2FA មិនត្រឹមត្រូវ ឬផុតកំណត់។",
                "emailInUse": "អ៊ីមែលនេះបានចុះឈ្មោះរួចហើយ។",
                "enterCode": "សូមបញ្ចូលលេខកូដ ៦ តួ ឬ recovery code។",
                "fillAllFields": "សូមបំពេញគ្រប់ប្រអប់។",
                "tooManyAttempts": "ព្យាយាមច្រើនដងពេក។ សូមរង់ចាំបន្តិចទៀត។",
            },
        }
    },
}

DEFAULT_LANG = "en"


def get_locale():
    lang = request.args.get("lang") or session.get("lang")
    if lang not in SUPPORTED:
        lang = DEFAULT_LANG
    return lang


def translate(key, default=None, lang=None):
    lang = lang or get_locale()
    node = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANG])
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            node = None
            break
    if node is None:
        return default if default is not None else key
    return node


def init_app(app):
    from datetime import datetime, timezone

    @app.context_processor
    def inject_globals():
        return {
            "t": translate,
            "lang": get_locale(),
            "now": datetime.now(timezone.utc),
        }
