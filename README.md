# Systema — Система Дня

Single-file HTML5 додаток (українською): **Душа & стійкість, щогодинний рух 13:00–21:00, «Тренувальна зона» (Convict Conditioning, 6 вправ × 10 рівнів у 3D), англійська 15 хв + SRS-фрази, кар'єра TPM/OKR, синхронізація Google Drive**. Працює офлайн, стан у `localStorage`.

## Мобільний інтерфейс (телефон)

- На екранах до 640px базовий шрифт збільшено з 16px до 18px (усі розміри Tailwind ростуть пропорційно), дрібні підписи 9–11px підняті до 11–13px, увімкнено pinch-zoom.
- Навігація з 8 розділів на телефоні стає нижньою панеллю вкладок (як у застосунку): кожен розділ — окремий екран, перемикання прокручує сторінку догори. На десктопі вигляд без змін.

## Готовий Android APK

- **Завантажити:** [`releases/systema-dnya-1.1-debug.apk`](releases/systema-dnya-1.1-debug.apk) (debug-підпис, встановлюється напряму на телефон; зібрано з мобільним інтерфейсом: більший шрифт + нижня панель екранів)
- Package: `ua.yusyp.sistemadnya`, версія `1.1` (versionCode 2), minSdk 24, targetSdk 36

## Джерело

- [`index.html`](index.html) — увесь додаток в одному файлі (без бекенду)

## Перезібрати APK локально (Capacitor)

```bash
npm install
mkdir -p www && cp index.html www/index.html
npx cap add android
npx cap sync android
cd android && ./gradlew assembleDebug
# APK: android/app/build/outputs/apk/debug/app-debug.apk
```

Потрібні: JDK 21+, Android SDK (platforms;android-36, build-tools;36.0.0), Node.js 20+.
Зібрано у CI-середовищі: Temurin JDK 21.0.13 + Android SDK 36 + Capacitor 8.6.2 + Gradle 8.14.3.

## PWA (без APK)

Відкрий `index.html` на HTTPS-хостингу (GitHub Pages) → «Додати на головний екран» — або згенеруй APK через PWABuilder.
