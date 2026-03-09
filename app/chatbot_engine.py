"""
Intelligent Chatbot Engine — Gemini-first with DB context injection.
"""

import logging
import os
import re
import requests
from typing import Optional
from datetime import datetime
from sqlalchemy import and_, or_
from requests.exceptions import RequestException, Timeout, ConnectionError as RequestsConnectionError

from app import db
from app.models import User, StudentProfile, Opportunity, Application

logger = logging.getLogger(__name__)


def _company_label(opp):
    if not opp:
        return "Unknown Company"
    return opp.company_name or getattr(opp, "organizer", None) or "Unknown Company"


class ChatbotEngine:

    _DB_KEYWORDS = {
        "opportunity", "opportunities", "job", "jobs", "opening", "openings",
        "internship", "internships", "drive", "drives", "recruitment",
        "application", "applied", "status", "eligible", "eligibility",
        "placement", "statistics", "stats", "branch", "cgpa", "gpa",
        "student", "deadline", "upcoming", "company", "companies",
        "requirement", "requirements", "criteria", "skills",
    }

    def __init__(self, session=None):
        self.session = session or db.session
        self.gemini_api_key = (
            os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        ).strip()
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
        self.gemini_api_base = os.getenv(
            "GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta"
        ).rstrip("/")

    def process_query(self, user_message, user_id=None, conversation_history=None):
        if not user_message or not isinstance(user_message, str):
            return self._err("Please provide a valid message.")

        user_message = user_message.strip()
        if not user_message:
            return self._err("Please provide a valid message.")

        greeting = self._check_greeting(user_message)
        if greeting:
            return greeting

        try:
            admin_result = self._admin_shortcuts(user_message, user_id)
            if admin_result:
                return admin_result

            db_context = self._build_db_context(user_message, user_id)

            answer = None
            method = None
            provider_errors = {}

            if self.gemini_api_key:
                answer, gemini_error = self._call_gemini(user_message, db_context, conversation_history)
                if answer:
                    method = "gemini"
                elif gemini_error:
                    provider_errors["gemini"] = gemini_error
            else:
                provider_errors["gemini"] = "missing_api_key"

            if not answer:
                mistral_key = os.getenv("MISTRAL_API_KEY", "").strip()
                if mistral_key:
                    answer, mistral_error = self._call_mistral(
                        user_message, db_context, mistral_key, conversation_history
                    )
                    if answer:
                        method = "mistral"
                    elif mistral_error:
                        provider_errors["mistral"] = mistral_error
                else:
                    provider_errors["mistral"] = "missing_api_key"

            if not answer:
                fallback = self._db_only_answer(user_message, user_id)
                if fallback.get("context") == "ai_unavailable":
                    error_summary = self._format_provider_errors(provider_errors)
                    fallback["ai_error"] = error_summary
                    logger.warning(
                        "AI service unavailable | user_id=%s | query=%r | details=%s",
                        user_id,
                        user_message[:160],
                        error_summary,
                    )
                return fallback

            return {
                "answer": answer,
                "success": True,
                "context": "ai_with_db_context",
                "intent": "user_query",
                "extraction_method": method,
            }

        except Exception as exc:
            logger.error("Query processing error: %s", exc, exc_info=True)
            return self._err("An error occurred while processing your request. Please try again.")

    @staticmethod
    def _extract_threshold(message):
        if not message:
            return None
        num = re.search(r"(\d+(?:\.\d+)?)", message.lower())
        if not num:
            return None
        try:
            return float(num.group(1))
        except ValueError:
            return None

    @staticmethod
    def _looks_like_cgpa_filter_query(message):
        msg = (message or "").lower()
        if ("cgpa" not in msg and "gpa" not in msg):
            return False
        if not re.search(r"(\d+(?:\.\d+)?)", msg):
            return False

        admin_cues = [
            "student", "students", "list", "show", "find",
            "more than", "above", "greater than", "at least",
        ]
        if any(cue in msg for cue in admin_cues):
            return True

        if re.search(r"(?:>=|>|<=|<|\+)\s*\d", msg):
            return True
        return bool(re.search(r"\d+(?:\.\d+)?\s*\+", msg))

    @staticmethod
    def _extract_http_error(resp):
        try:
            payload = resp.json()
            err = payload.get("error")
            if isinstance(err, dict):
                msg = err.get("message") or err.get("status") or str(err)
                return str(msg).replace("\n", " ")[:240]
            if isinstance(err, str):
                return err.replace("\n", " ")[:240]
        except ValueError:
            pass

        body = (resp.text or "").replace("\n", " ").strip()
        return body[:240] if body else "no_error_body"

    @staticmethod
    def _format_provider_errors(provider_errors):
        if not provider_errors:
            return "no_provider_attempted"
        parts = []
        for provider, reason in provider_errors.items():
            parts.append("{}: {}".format(provider, reason))
        return " | ".join(parts)

    def _call_gemini(self, user_message, db_context, history=None):
        if not self.gemini_api_key:
            return None, "missing_api_key"

        try:

            system_prompt = self._system_prompt()
            user_turn = self._build_user_turn(user_message, db_context)

            contents = []
            if history:
                for turn in history[-6:]:
                    role = "user" if turn.get("role") == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": turn["content"]}]})
            contents.append({"role": "user", "parts": [{"text": user_turn}]})

            endpoint = "{}/models/{}:generateContent".format(
                self.gemini_api_base, self.gemini_model
            )
            payload = {
                "systemInstruction": {
                    "role": "system",
                    "parts": [{"text": system_prompt}],
                },
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.5,
                    "topP": 0.95,
                    "maxOutputTokens": 900,
                },
            }

            resp = requests.post(
                endpoint,
                params={"key": self.gemini_api_key},
                json=payload,
                timeout=25,
            )
            if resp.status_code != 200:
                err_detail = self._extract_http_error(resp)
                logger.warning(
                    "Gemini request failed | status=%s | model=%s | error=%s",
                    resp.status_code,
                    self.gemini_model,
                    err_detail,
                )
                return None, "http_{}: {}".format(resp.status_code, err_detail)

            data = resp.json()
            candidates = data.get("candidates") or []
            if not candidates:
                logger.warning("Gemini response missing candidates.")
                return None, "no_candidates"

            parts = (candidates[0].get("content") or {}).get("parts") or []
            text = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
            text = text.replace("```", "").strip()
            if not text:
                logger.warning("Gemini response text was empty after parsing.")
                return None, "empty_text"
            return text, None

        except Timeout:
            logger.error("Gemini request timed out after 25 seconds.")
            return None, "timeout"
        except RequestsConnectionError as exc:
            logger.error("Gemini connection error: %s", exc)
            return None, "connection_error"
        except RequestException as exc:
            logger.error("Gemini request exception: %s", exc)
            return None, "request_exception"
        except ValueError as exc:
            logger.error("Gemini returned invalid JSON: %s", exc)
            return None, "invalid_json"
        except Exception as exc:
            logger.error("Gemini unexpected error: %s", exc, exc_info=True)
            return None, "unexpected_error"

    def _call_mistral(self, user_message, db_context, api_key, history=None):
        try:
            system_prompt = self._system_prompt()
            user_turn = self._build_user_turn(user_message, db_context)

            messages = [{"role": "system", "content": system_prompt}]
            if history:
                for turn in history[-6:]:
                    messages.append({
                        "role": turn.get("role", "user"),
                        "content": turn["content"]
                    })
            messages.append({"role": "user", "content": user_turn})

            resp = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": "Bearer {}".format(api_key)},
                json={
                    "model": "mistral-small-latest",
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 900,
                    "top_p": 0.95,
                },
                timeout=20,
            )
            if resp.status_code != 200:
                err_detail = self._extract_http_error(resp)
                logger.warning(
                    "Mistral request failed | status=%s | error=%s",
                    resp.status_code,
                    err_detail,
                )
                return None, "http_{}: {}".format(resp.status_code, err_detail)

            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            text = text.replace("```", "").strip()
            if not text:
                logger.warning("Mistral response text was empty after parsing.")
                return None, "empty_text"
            return text, None

        except Timeout:
            logger.error("Mistral request timed out after 20 seconds.")
            return None, "timeout"
        except RequestsConnectionError as exc:
            logger.error("Mistral connection error: %s", exc)
            return None, "connection_error"
        except RequestException as exc:
            logger.error("Mistral request exception: %s", exc)
            return None, "request_exception"
        except ValueError as exc:
            logger.error("Mistral returned invalid JSON: %s", exc)
            return None, "invalid_json"
        except Exception as exc:
            logger.error("Mistral unexpected error: %s", exc, exc_info=True)
            return None, "unexpected_error"

    def _system_prompt(self):
        return (
            "You are TPC Ask, an intelligent assistant for a college Training & Placement Cell (TPC).\n\n"
            "YOUR ROLE:\n"
            "- Help students find job/internship opportunities, check eligibility, track applications,\n"
            "  understand deadlines, and get placement advice.\n"
            "- Help admins get analytics, student lists, and placement statistics.\n\n"
            "HOW TO USE THE DATABASE CONTEXT:\n"
            "- You will receive a DATABASE CONTEXT section with real, live data from the portal.\n"
            "- Always prioritise this data over your general knowledge.\n"
            "- If the context contains relevant information, use it directly and specifically.\n"
            "- If the context is empty or irrelevant, say so honestly and offer general placement guidance.\n\n"
            "RESPONSE STYLE:\n"
            "- Be concise, friendly, and specific. Use bullet points for lists.\n"
            "- Always mention real company names, CTCs, deadlines from the context when available.\n"
            "- If the student asks a follow-up, use the conversation history to answer coherently.\n"
            "- Never make up data. If something is not in the context, say you do not have that info.\n"
            "- Keep answers under 400 words unless the user asks for a detailed breakdown.\n"
        )

    def _build_user_turn(self, user_message, db_context):
        ctx = db_context.strip() if db_context else "No specific database records found for this query."
        sep = "=" * 60
        return (
            "DATABASE CONTEXT (live data from the placement portal):\n"
            "{sep}\n"
            "{ctx}\n"
            "{sep}\n\n"
            "STUDENT/USER QUESTION: {msg}\n\n"
            "Please answer using the database context above. "
            "If the context does not contain enough information, say so and give general guidance."
        ).format(sep=sep, ctx=ctx, msg=user_message)

    def _build_db_context(self, user_message, user_id=None):
        parts = []
        msg = user_message.lower()

        # Student profile
        if user_id:
            try:
                user = User.query.get(user_id)
                profile = StudentProfile.query.filter_by(user_id=user_id).first()
                if user and profile:
                    parts.append(
                        "[LOGGED-IN STUDENT]\n"
                        "  Name   : {}\n"
                        "  Branch : {}\n"
                        "  CGPA   : {}\n"
                        "  Skills : {}\n"
                        "  Resume : {}".format(
                            user.username,
                            profile.branch,
                            profile.cgpa,
                            profile.skills or "Not specified",
                            "Uploaded" if profile.resume_link else "Not uploaded",
                        )
                    )
            except Exception:
                pass

        # Opportunities
        placement_words = [
            "opportunit", "job", "opening", "intern", "drive", "recruit",
            "compan", "apply", "eligib", "deadline", "upcoming", "position",
            "ctc", "salary", "package", "placement", "hire", "hiring",
        ]
        generic_words = ["what", "show", "list", "find", "tell"]
        off_topic = all(w not in msg for w in placement_words)

        if not off_topic or any(w in msg for w in generic_words):
            try:
                opps = Opportunity.query.order_by(Opportunity.created_at.desc()).limit(20).all()
                if opps:
                    lines = ["[OPPORTUNITIES - {} most recent]".format(len(opps))]
                    for o in opps[:12]:
                        dl = o.deadline.strftime("%Y-%m-%d") if o.deadline else "N/A"
                        days_left = ""
                        if o.deadline:
                            days_left = "{}d left".format((o.deadline - datetime.utcnow()).days)
                        ctc = "{} {}".format(chr(8377), o.ctc) if o.ctc else "Not disclosed"
                        lines.append(
                            "  * [{}] {} @ {} | CTC: {} | Deadline: {} {} | Min CGPA: {} | Branches: {}".format(
                                o.type,
                                o.title,
                                _company_label(o),
                                ctc,
                                dl,
                                days_left,
                                o.min_cgpa or "None",
                                o.allowed_branches or "All",
                            )
                        )
                    if len(opps) > 12:
                        lines.append("  ... and {} more in the portal.".format(len(opps) - 12))
                    parts.append("\n".join(lines))
            except Exception:
                pass

        # Eligible opportunities
        eligib_words = ["eligib", "qualify", "can i apply", "suitable", "my profile"]
        if user_id and any(w in msg for w in eligib_words):
            try:
                profile = StudentProfile.query.filter_by(user_id=user_id).first()
                if profile:
                    eligible = Opportunity.query.filter(
                        and_(
                            or_(
                                Opportunity.min_cgpa <= profile.cgpa,
                                Opportunity.min_cgpa.is_(None),
                            ),
                            or_(
                                Opportunity.allowed_branches.contains(profile.branch),
                                Opportunity.allowed_branches.is_(None),
                            ),
                            Opportunity.deadline > datetime.utcnow(),
                        )
                    ).all()
                    if eligible:
                        lines = ["[ELIGIBLE OPPORTUNITIES for {} / CGPA {}]".format(
                            profile.branch, profile.cgpa
                        )]
                        for o in eligible[:8]:
                            dl = o.deadline.strftime("%Y-%m-%d") if o.deadline else "N/A"
                            lines.append("  * {} @ {} | Deadline: {}".format(
                                o.title, _company_label(o), dl
                            ))
                        parts.append("\n".join(lines))
                    else:
                        parts.append("[ELIGIBLE OPPORTUNITIES] None found matching your profile right now.")
            except Exception:
                pass

        # Student applications
        app_words = ["application", "applied", "status", "track", "my application"]
        if user_id and any(w in msg for w in app_words):
            try:
                apps = Application.query.filter_by(student_id=user_id).order_by(
                    Application.applied_at.desc()
                ).all()
                if apps:
                    status_counts = {}
                    lines = ["[YOUR APPLICATIONS - {} total]".format(len(apps))]
                    for app in apps[:10]:
                        opp = Opportunity.query.get(app.opportunity_id)
                        status_counts[app.status] = status_counts.get(app.status, 0) + 1
                        company = _company_label(opp) if opp else "Unknown"
                        title = opp.title if opp else "N/A"
                        lines.append("  * {} @ {} -> {}".format(title, company, app.status))
                    summary = ", ".join("{}: {}".format(s, c) for s, c in status_counts.items())
                    lines.append("  Summary: {}".format(summary))
                    parts.append("\n".join(lines))
                else:
                    parts.append("[YOUR APPLICATIONS] No applications found yet.")
            except Exception:
                pass

        # Upcoming drives
        drive_words = ["upcoming", "drive", "recruit", "next week", "next month", "deadline", "soon"]
        if any(w in msg for w in drive_words):
            try:
                upcoming = (
                    Opportunity.query.filter(Opportunity.deadline > datetime.utcnow())
                    .order_by(Opportunity.deadline)
                    .limit(10)
                    .all()
                )
                if upcoming:
                    lines = ["[UPCOMING DRIVES - next {}]".format(len(upcoming))]
                    for o in upcoming:
                        dl = o.deadline.strftime("%Y-%m-%d") if o.deadline else "N/A"
                        days = (o.deadline - datetime.utcnow()).days if o.deadline else "?"
                        lines.append("  * {} @ {} | {} ({} days left)".format(
                            o.title, _company_label(o), dl, days
                        ))
                    parts.append("\n".join(lines))
            except Exception:
                pass

        # Placement statistics
        stat_words = ["statistic", "stat", "placement rate", "placed", "how many", "percentage", "rate"]
        if any(w in msg for w in stat_words):
            try:
                total_students = StudentProfile.query.count()
                placed = (
                    db.session.query(Application)
                    .filter_by(status="Selected")
                    .distinct(Application.student_id)
                    .count()
                )
                total_apps = Application.query.count()
                pending = Application.query.filter_by(status="Applied").count()
                rate = (placed / total_students * 100) if total_students else 0
                total_opps = Opportunity.query.count()
                parts.append(
                    "[PLACEMENT STATISTICS]\n"
                    "  Total students     : {}\n"
                    "  Placed students    : {}\n"
                    "  Placement rate     : {:.1f}%\n"
                    "  Total opportunities: {}\n"
                    "  Total applications : {}\n"
                    "  Pending (Applied)  : {}".format(
                        total_students, placed, rate, total_opps, total_apps, pending
                    )
                )
            except Exception:
                pass

        # Branch analytics
        if "branch" in msg and any(w in msg for w in ["analytic", "analysis", "stat", "breakdown"]):
            try:
                rows = (
                    db.session.query(
                        StudentProfile.branch,
                        db.func.count(StudentProfile.id),
                        db.func.avg(StudentProfile.cgpa),
                    )
                    .group_by(StudentProfile.branch)
                    .all()
                )
                if rows:
                    lines = ["[BRANCH ANALYTICS]"]
                    for branch, cnt, avg_cgpa in rows:
                        lines.append("  * {}: {} students, avg CGPA {:.2f}".format(
                            branch, cnt, avg_cgpa
                        ))
                    parts.append("\n".join(lines))
            except Exception:
                pass

        # Portal snapshot fallback
        if not parts:
            try:
                total_opps = Opportunity.query.count()
                active_opps = Opportunity.query.filter(
                    Opportunity.deadline > datetime.utcnow()
                ).count()
                total_students = StudentProfile.query.count()
                parts.append(
                    "[PORTAL SNAPSHOT]\n"
                    "  Total opportunities: {} ({} still open)\n"
                    "  Total students: {}\n"
                    "  Placement cell is active.".format(
                        total_opps, active_opps, total_students
                    )
                )
            except Exception:
                pass

        return "\n\n".join(parts)

    def _admin_shortcuts(self, message, user_id):
        msg = message.lower()
        if self._looks_like_cgpa_filter_query(msg):
            threshold = self._extract_threshold(msg)
            if threshold is not None:
                if not user_id:
                    return self._denied("Please log in as an admin to search students by CGPA.")
                user = User.query.get(user_id)
                is_admin = user and user.role.lower() == "admin"
                if is_admin:
                    return self._students_by_cgpa(threshold)
                return self._denied("Student CGPA searches are available to admins only.")

        if not user_id:
            return None

        user = User.query.get(user_id)
        is_admin = user and user.role.lower() == "admin"

        if "student" in msg and any(k in msg for k in ["list", "show", "all", "students"]):
            if is_admin:
                return self._list_students()
            return self._denied("Student listings are available to admins only.")

        if "applicants" in msg and "list" in msg:
            if is_admin:
                return self._list_applicants()
            return self._denied("Listing all applicants is an admin-only action.")

        return None

    def _db_only_answer(self, message, user_id=None):
        msg = message.lower()

        if self._looks_like_cgpa_filter_query(msg):
            threshold = self._extract_threshold(msg)
            if threshold is not None:
                if not user_id:
                    return self._denied("Please log in as an admin to search students by CGPA.")
                user = User.query.get(user_id)
                if user and user.role.lower() == "admin":
                    return self._students_by_cgpa(threshold)
                return self._denied("Student CGPA searches are available to admins only.")

        if any(w in msg for w in ["upcoming", "drive", "drives", "recruit"]):
            upcoming = (
                Opportunity.query.filter(Opportunity.deadline > datetime.utcnow())
                .order_by(Opportunity.deadline)
                .limit(8)
                .all()
            )
            if not upcoming:
                return self._ok("No upcoming drives found.", "upcoming_drives")
            lines = ["Upcoming drives:"]
            for o in upcoming:
                dl = o.deadline.strftime("%Y-%m-%d") if o.deadline else "N/A"
                lines.append("* {} @ {} - deadline {}".format(o.title, _company_label(o), dl))
            return self._ok("\n".join(lines), "upcoming_drives")

        if any(w in msg for w in ["opportunit", "job", "opening", "intern"]):
            opps = Opportunity.query.order_by(Opportunity.created_at.desc()).limit(6).all()
            if not opps:
                return self._ok("No opportunities found.", "search")
            lines = ["Found {} opportunities. Recent ones:".format(Opportunity.query.count())]
            for o in opps:
                lines.append("* {} @ {}".format(o.title, _company_label(o)))
            return self._ok("\n".join(lines), "search")

        if user_id and any(w in msg for w in ["application", "applied", "status"]):
            apps = Application.query.filter_by(student_id=user_id).all()
            if not apps:
                return self._ok("You haven't applied to any opportunities yet.", "application_status")
            lines = ["You have {} application(s):".format(len(apps))]
            for app in apps[:8]:
                opp = Opportunity.query.get(app.opportunity_id)
                lines.append("* {} @ {} -> {}".format(
                    opp.title if opp else "N/A", _company_label(opp), app.status
                ))
            return self._ok("\n".join(lines), "application_status")

        if any(w in msg for w in ["stat", "placement", "rate", "placed"]):
            total = StudentProfile.query.count()
            placed = (
                db.session.query(Application)
                .filter_by(status="Selected")
                .distinct(Application.student_id)
                .count()
            )
            rate = (placed / total * 100) if total else 0
            return self._ok(
                "Placement stats:\n* Total students: {}\n* Placed: {}\n* Rate: {:.1f}%".format(
                    total, placed, rate
                ),
                "placement_stats",
            )

        return {
            "answer": (
                "I could not connect to the AI service right now. "
                "Try asking about: opportunities, your applications, upcoming drives, or placement stats."
            ),
            "success": False,
            "context": "ai_unavailable",
            "intent": None,
        }

    def _check_greeting(self, message):
        normalized = re.sub(r"[^a-z\s]", " ", message.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()

        greetings = {
            "hello": (
                "Hello! I'm your Training & Placement Assistant. "
                "I can help you search for opportunities, check eligibility, track applications, and more. "
                "What would you like to know?"
            ),
            "hi": "Hi there! How can I assist you today?",
            "hey": "Hey! Ask me anything about placement opportunities or your applications.",
            "thanks": "You're welcome! Let me know if you need anything else.",
            "thank you": "You're welcome! Is there anything else I can help with?",
            "bye": "Goodbye! Good luck with your placements!",
            "goodbye": "Goodbye! Feel free to come back anytime.",
            "help": self._help_text(),
        }
        aliases = {
            "hello there": "hello",
            "hi there": "hi",
            "thankyou": "thank you",
            "thanks a lot": "thanks",
            "help me": "help",
        }

        key = aliases.get(normalized, normalized)
        resp = greetings.get(key)
        if resp:
            return {"answer": resp, "success": True, "context": "greeting", "intent": None}
        return None

    def _students_by_cgpa(self, threshold):
        rows = (
            db.session.query(User.username, User.email, StudentProfile.branch, StudentProfile.cgpa)
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .filter(StudentProfile.cgpa >= threshold)
            .order_by(StudentProfile.cgpa.desc())
            .limit(25)
            .all()
        )
        if not rows:
            return self._ok("No students found with CGPA >= {}.".format(threshold), "student_search")
        lines = ["Students with CGPA >= {}:".format(threshold)]
        for s in rows:
            lines.append("* {} ({}) - {}, CGPA {}".format(s.username, s.email, s.branch, s.cgpa))
        return self._ok("\n".join(lines), "student_search")

    def _list_students(self):
        rows = (
            db.session.query(User.username, User.email, StudentProfile.branch, StudentProfile.cgpa)
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .order_by(User.username)
            .limit(25)
            .all()
        )
        if not rows:
            return self._ok("No students found.", "list_students")
        lines = ["Students:"]
        for s in rows:
            lines.append("* {} ({}) - {}, CGPA {}".format(s.username, s.email, s.branch, s.cgpa))
        return self._ok("\n".join(lines), "list_students")

    def _list_applicants(self):
        rows = (
            db.session.query(User.username, User.email, Application.status, Opportunity.title)
            .join(Application, Application.student_id == User.id)
            .join(Opportunity, Opportunity.id == Application.opportunity_id, isouter=True)
            .limit(25)
            .all()
        )
        if not rows:
            return self._ok("No applicants found.", "list_applicants")
        lines = ["Applicants:"]
        for uname, email, status, title in rows:
            lines.append("* {} ({}) - {} - {}".format(uname, email, status, title or "N/A"))
        return self._ok("\n".join(lines), "list_applicants")

    @staticmethod
    def _ok(answer, context, intent=None):
        return {"answer": answer, "success": True, "context": context, "intent": intent or context}

    @staticmethod
    def _err(answer):
        return {"answer": answer, "success": False, "context": "error", "intent": None}

    @staticmethod
    def _denied(answer):
        return {"answer": answer, "success": False, "context": "permission_denied", "intent": None}

    @staticmethod
    def _help_text():
        return (
            "I'm your AI-powered Training & Placement Assistant! Here's what I can do:\n\n"
            "Opportunities:\n"
            "* Show me all open jobs\n"
            "* Find internships with CTC above 6 LPA\n"
            "* Which companies are recruiting this month?\n\n"
            "Your Profile:\n"
            "* Am I eligible for any positions?\n"
            "* What's my application status?\n"
            "* Which drives have I applied to?\n\n"
            "Placement Info:\n"
            "* Show placement statistics\n"
            "* What are the upcoming recruitment drives?\n\n"
            "Admin (admin users only):\n"
            "* List students with CGPA above 8\n"
            "* Show branch-wise analytics\n"
            "* List all applicants\n\n"
            "Just ask naturally - I'll understand!"
        )
