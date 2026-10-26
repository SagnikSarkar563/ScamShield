import re
from urllib.parse import urlparse


# ============================================================
# SCAMSHIELD - URL ANALYSIS ENGINE
# ============================================================

SUSPICIOUS_KEYWORDS = [
    "verify",
    "verification",
    "kyc",
    "secure",
    "security",
    "login",
    "signin",
    "account",
    "update",
    "confirm",
    "refund",
    "reward",
    "prize",
    "cashback",
    "payment",
    "wallet",
    "bank",
    "blocked",
    "unlock",
    "urgent",
    "support",
    "customer-care",
    "customer-support",
    "otp",
]

SUSPICIOUS_TLDS = {
    "top",
    "xyz",
    "click",
    "link",
    "live",
    "shop",
    "online",
    "site",
    "icu",
    "buzz",
}


# ============================================================
# URL EXTRACTION
# ============================================================

def extract_urls(text):
    """
    Extract HTTP/HTTPS URLs from a message.
    """

    if not text:
        return []

    pattern = r"https?://[^\s<>\"]+"

    urls = re.findall(pattern, text)

    cleaned_urls = []

    for url in urls:
        # Remove punctuation that commonly appears after URLs
        url = url.rstrip(".,!?;:)']\"")

        if url:
            cleaned_urls.append(url)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(cleaned_urls))


# ============================================================
# IP ADDRESS DETECTION
# ============================================================

def is_ip_address(hostname):
    """
    Determine whether the hostname is an IPv4 address.
    """

    if not hostname:
        return False

    pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"

    if not re.match(pattern, hostname):
        return False

    # Validate each octet
    try:
        octets = hostname.split(".")

        return all(
            0 <= int(octet) <= 255
            for octet in octets
        )

    except ValueError:
        return False


# ============================================================
# SINGLE URL ANALYSIS
# ============================================================

def analyze_url(url):
    """
    Analyze a single URL and return structured security indicators.
    """

    result = {
        "url": url,
        "is_valid": False,
        "risk_score": 0,
        "risk_level": "LOW",
        "findings": [],
        "features": {}
    }

    try:

        # ----------------------------------------------------
        # Parse URL
        # ----------------------------------------------------

        parsed = urlparse(url)

        if parsed.scheme not in ["http", "https"] or not parsed.netloc:

            result["findings"].append(
                "Invalid or unsupported URL."
            )

            result["risk_score"] = 70
            result["risk_level"] = "HIGH"

            return result

        result["is_valid"] = True

        hostname = parsed.hostname.lower() if parsed.hostname else ""
        path = parsed.path.lower()
        full_url = url.lower()

        # Determine whether hostname is an IP
        ip_address = is_ip_address(hostname)

        # ----------------------------------------------------
        # Basic URL features
        # ----------------------------------------------------

        result["features"]["https"] = (
            parsed.scheme == "https"
        )

        result["features"]["hostname"] = hostname

        result["features"]["url_length"] = len(url)

        result["features"]["is_ip_address"] = ip_address

        # ----------------------------------------------------
        # Subdomain count
        # ----------------------------------------------------

        if ip_address:

            # IP addresses do not have subdomains
            subdomain_count = 0

        else:

            hostname_parts = hostname.split(".")

            subdomain_count = max(
                len(hostname_parts) - 2,
                0
            )

        result["features"]["subdomain_count"] = subdomain_count

        # ----------------------------------------------------
        # HTTPS
        # ----------------------------------------------------

        if parsed.scheme != "https":

            result["risk_score"] += 15

            result["findings"].append(
                "The URL does not use HTTPS."
            )

        # ----------------------------------------------------
        # IP address instead of domain
        # ----------------------------------------------------

        if ip_address:

            result["risk_score"] += 30

            result["findings"].append(
                "The URL uses an IP address instead of a normal domain name."
            )

        # ----------------------------------------------------
        # URL length
        # ----------------------------------------------------

        if len(url) > 100:

            result["risk_score"] += 10

            result["findings"].append(
                "The URL is unusually long."
            )

        if len(url) > 200:

            result["risk_score"] += 10

            result["findings"].append(
                "The URL is extremely long and may contain obfuscated parameters."
            )

        # ----------------------------------------------------
        # Suspicious @ symbol
        # ----------------------------------------------------

        if "@" in url:

            result["risk_score"] += 25

            result["findings"].append(
                "The URL contains '@', which can hide the actual destination."
            )

        # ----------------------------------------------------
        # Repeated path separators
        # ----------------------------------------------------

        if "//" in parsed.path:

            result["risk_score"] += 10

            result["findings"].append(
                "The URL contains unusual repeated path separators."
            )

        # ----------------------------------------------------
        # Excessive subdomains
        # ----------------------------------------------------

        if subdomain_count >= 3:

            result["risk_score"] += 15

            result["findings"].append(
                "The domain contains an unusually high number of subdomains."
            )

        # ----------------------------------------------------
        # Suspicious keywords
        # ----------------------------------------------------

        keyword_matches = []

        for keyword in SUSPICIOUS_KEYWORDS:

            if keyword in full_url:

                keyword_matches.append(keyword)

        result["features"]["suspicious_keywords"] = (
            keyword_matches
        )

        if keyword_matches:

            keyword_score = min(
                len(keyword_matches) * 5,
                20
            )

            result["risk_score"] += keyword_score

            result["findings"].append(
                "The URL contains suspicious security, payment, "
                "account, verification, or urgency-related keywords."
            )

        # ----------------------------------------------------
        # TLD detection
        # ----------------------------------------------------

        tld = ""

        if not ip_address:

            hostname_parts = hostname.split(".")

            if len(hostname_parts) >= 2:

                tld = hostname_parts[-1]

        result["features"]["tld"] = tld

        # ----------------------------------------------------
        # Suspicious TLD
        # ----------------------------------------------------

        if tld in SUSPICIOUS_TLDS:

            result["risk_score"] += 15

            result["findings"].append(
                f"The domain uses the potentially suspicious '.{tld}' TLD."
            )

        # ----------------------------------------------------
        # Punycode / Internationalized Domain Name
        # ----------------------------------------------------

        if "xn--" in hostname:

            result["risk_score"] += 20

            result["findings"].append(
                "The domain uses punycode, which can sometimes "
                "be used for look-alike domains."
            )

        # ----------------------------------------------------
        # Domain hyphens
        # ----------------------------------------------------

        hyphen_count = hostname.count("-")

        result["features"]["hyphen_count"] = (
            hyphen_count
        )

        if hyphen_count >= 3:

            result["risk_score"] += 10

            result["findings"].append(
                "The domain contains many hyphens."
            )

        # ----------------------------------------------------
        # Suspicious path keywords
        # ----------------------------------------------------

        path_keywords = [
            "login",
            "verify",
            "kyc",
            "otp",
            "password",
            "signin",
            "account",
            "update",
            "payment",
            "refund",
        ]

        path_matches = []

        for keyword in path_keywords:

            if keyword in path:

                path_matches.append(keyword)

        result["features"]["path_keywords"] = (
            path_matches
        )

        if path_matches:

            path_score = min(
                len(path_matches) * 5,
                15
            )

            result["risk_score"] += path_score

            result["findings"].append(
                "The URL path contains sensitive account "
                "or verification keywords."
            )

        # ----------------------------------------------------
        # Query parameter analysis
        # ----------------------------------------------------

        query = parsed.query

        result["features"]["has_query"] = bool(query)

        if len(query) > 100:

            result["risk_score"] += 5

            result["findings"].append(
                "The URL contains unusually long query parameters."
            )

        # ----------------------------------------------------
        # Fragment analysis
        # ----------------------------------------------------

        result["features"]["has_fragment"] = bool(
            parsed.fragment
        )

        # ----------------------------------------------------
        # Final score
        # ----------------------------------------------------

        result["risk_score"] = min(
            result["risk_score"],
            100
        )

        # ----------------------------------------------------
        # Risk level
        # ----------------------------------------------------

        if result["risk_score"] < 25:

            result["risk_level"] = "LOW"

        elif result["risk_score"] < 50:

            result["risk_level"] = "MEDIUM"

        elif result["risk_score"] < 75:

            result["risk_level"] = "HIGH"

        else:

            result["risk_level"] = "CRITICAL"

        return result

    except Exception as error:

        result["findings"].append(
            f"URL analysis error: {str(error)}"
        )

        result["risk_score"] = 80
        result["risk_level"] = "HIGH"

        return result


# ============================================================
# MESSAGE URL ANALYSIS
# ============================================================

def analyze_text_urls(text):
    """
    Extract and analyze every URL present in a message.
    """

    urls = extract_urls(text)

    results = []

    for url in urls:

        analysis = analyze_url(url)

        results.append(analysis)

    return results


# ============================================================
# SUMMARY FUNCTION
# ============================================================

def summarize_url_analysis(results):
    """
    Generate an overall URL risk summary from multiple URLs.
    """

    if not results:

        return {
            "url_count": 0,
            "highest_risk_score": 0,
            "highest_risk_level": "LOW",
            "overall_findings": []
        }

    highest_score = max(
        result["risk_score"]
        for result in results
    )

    # Determine overall risk level
    if highest_score < 25:

        highest_level = "LOW"

    elif highest_score < 50:

        highest_level = "MEDIUM"

    elif highest_score < 75:

        highest_level = "HIGH"

    else:

        highest_level = "CRITICAL"

    all_findings = []

    for result in results:

        for finding in result["findings"]:

            if finding not in all_findings:

                all_findings.append(finding)

    return {
        "url_count": len(results),
        "highest_risk_score": highest_score,
        "highest_risk_level": highest_level,
        "overall_findings": all_findings
    }


# ============================================================
# DISPLAY FUNCTION
# ============================================================

def print_url_analysis(result):

    print("\n" + "-" * 70)
    print(f"URL: {result['url']}")
    print("-" * 70)

    print(
        f"Risk Score : {result['risk_score']}/100"
    )

    print(
        f"Risk Level : {result['risk_level']}"
    )

    print("\nFindings:")

    if result["findings"]:

        for finding in result["findings"]:

            print(f"  • {finding}")

    else:

        print(
            "  • No obvious suspicious indicators detected."
        )

    print("\nFeatures:")

    for key, value in result["features"].items():

        print(f"  • {key}: {value}")


# ============================================================
# TEST / DEMO
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("SCAMSHIELD - URL ANALYSIS ENGINE")
    print("=" * 70)

    test_urls = [

        # Normal HTTPS website
        "https://www.google.com",

        # IP address
        "http://192.168.1.10/login",

        # Suspicious banking/KYC URL
        "http://secure-bank-verify-kyc.xyz/login",

        # HTTPS but suspicious path
        "https://example.com/account/verify",

        # Long suspicious URL
        "http://secure-login-bank-verify.xyz/account/kyc/update?session=12345678901234567890",

        # Punycode example
        "https://xn--example-dma.com/login",
    ]

    for url in test_urls:

        result = analyze_url(url)

        print_url_analysis(result)

    # ========================================================
    # MESSAGE TEST
    # ========================================================

    print("\n\n")
    print("=" * 70)
    print("MESSAGE URL EXTRACTION TEST")
    print("=" * 70)

    test_message = (
        "Your bank account will be blocked today. "
        "Verify your KYC immediately using "
        "http://secure-bank-verify-kyc.xyz/login "
        "or your account will be suspended."
    )

    print("\nMessage:")
    print(test_message)

    url_results = analyze_text_urls(
        test_message
    )

    print("\nURLs detected:")

    if not url_results:

        print("  • No URLs detected.")

    else:

        for result in url_results:

            print(
                f"  • {result['url']}"
            )

    summary = summarize_url_analysis(
        url_results
    )

    print("\nURL Summary:")
    print(
        f"  • URL Count: {summary['url_count']}"
    )
    print(
        f"  • Highest Risk Score: "
        f"{summary['highest_risk_score']}/100"
    )
    print(
        f"  • Highest Risk Level: "
        f"{summary['highest_risk_level']}"
    )

    print("\nOverall Findings:")

    if summary["overall_findings"]:

        for finding in summary["overall_findings"]:

            print(f"  • {finding}")

    else:

        print(
            "  • No obvious suspicious URL indicators detected."
        )

    print("\n")
    print("=" * 70)
    print("URL ANALYSIS COMPLETE")
    print("=" * 70)