# Complaint Management System / Şikayet Yönetim Sistemi

##  English

###  Purpose

This is an **AI-powered complaint management system** designed to help organizations manage user feedback more efficiently. It includes automatic classification of Turkish complaints, a user-friendly frontend, a management dashboard, and AI-generated summary reports.

We encourage others to **integrate this system into their own infrastructure** and modify it as needed. The project is **completely open source**, and all contributions or customizations are welcome.

> We kindly ask for a **small credit or acknowledgment** (e.g., a citation, a thank-you note) if you use or build upon this project.

---

###  Overview of the Implementation

- **Frontend**: Angular-based, responsive UI with complaint submission, tracking, and management features.
- **Backend**: Django REST framework; handles complaint storage, user login, classification, and report generation.
- **AI Component**: Turkish complaint classification model (trained using LinearSVC) + LLM-powered (Groq / LLaMA-3) summarization module.
- **Dataset**: Custom-built, LLM-augmented Turkish dataset with 3899 samples across 6 complaint categories related to building management.

---

###  Things to Improve / Known Limitations

- ** Login System**: Currently, passwords are stored in **plain text** in the database. This should be replaced with proper password hashing (e.g., using bcrypt).
- ** Language Limitation**: The AI classifier only works for **Turkish** complaints. To support other languages, a multilingual or retrained model is required.
- ** Domain Limitation**: The AI model is specifically trained on **building management complaints**. If used in another sector, retraining with relevant data is recommended.

---

###  License & Usage

This project is **fully open-source**. You are free to use, modify, deploy, or integrate it in any way you'd like.

> **All we ask:** Please include a small **credit** somewhere if you benefit from this system.

---

##  Türkçe

###  Projenin Amacı

Bu proje, kurumların şikayet süreçlerini daha verimli yönetebilmeleri için geliştirilmiş **AI destekli bir şikayet yönetim sistemidir**. Kullanıcıların şikayetlerini kolayca iletebilmesi, yöneticilerin şikayetleri görüntüleyip raporlayabilmesi ve sınıflandırma modülüyle hızlı analiz yapılabilmesi amaçlanmıştır.

Projeyi kendi sistemlerinize **entegre ederek kullanabilir**, ihtiyacınıza göre özelleştirebilirsiniz. Proje **tamamen açık kaynaklıdır**, gönül rahatlığıyla kullanabilirsiniz.

> Tek beklentimiz: Kullanırsanız, **küçük bir teşekkür veya atıf** (örneğin bir teşekkür satırı ya da referans) eklerseniz mutlu oluruz.

---

###  Kısaca Nasıl Yaptık?

- **Frontend**: Angular ile geliştirildi. Şikayet gönderme, takip, yönetim paneli gibi modüller içeriyor.
- **Backend**: Django REST Framework kullanılarak geliştirildi. Şikayetlerin kaydı, kullanıcı girişi, sınıflandırma ve raporlama burada işleniyor.
- **Yapay Zeka Modülü**: Türkçe şikayetleri sınıflandıran bir LinearSVC modeli + Groq API üzerinden çalışan LLM (LLaMA-3) tabanlı rapor özeti oluşturucu.
- **Veri Kümesi**: ChatGPT, Gemini ve Grok kullanılarak oluşturulmuş, 3899 örnek içeren, özel bina şikayet veri kümesi.

---

###  Düzeltilmesi Gerekenler / Bilinen Eksikler

- ** Giriş Sistemi**: Şifreler şu anda **şifrelenmemiş şekilde** (plaintext) veri tabanında tutuluyor. Güvenlik açısından mutlaka hashleme (örneğin bcrypt) yapılmalı.
- ** Dil Kısıtı**: Sınıflandırma modeli sadece **Türkçe şikayetler** için çalışıyor. İngilizce veya diğer diller için yeniden eğitim gerekir.
- ** Sektörel Kısıt**: Model sadece **bina yönetimi şikayetleri** için eğitilmiştir. Başka sektörlerde kullanmak istenirse, uygun verilerle tekrar eğitilmesi önerilir.

---

###  Lisans & Kullanım

Bu proje **tamamen açık kaynaklıdır**. Dilediğiniz gibi kullanabilir, değiştirebilir veya entegre edebilirsiniz.

> **Tek isteğimiz:** Eğer projemizden faydalandıysanız, lütfen **küçük bir teşekkür veya atıf** bırakın 🙏

---

