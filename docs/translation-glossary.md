# Translation glossary

Terms the author has decided on. Every translation (UI, CV, articles, posts) uses them; a new decision is added
here first. Languages: en (source of the UI), es (neutral, for readers on every continent; Spain-only realia explained), ru, sr (**Latin script**, ekavian), uz (**Latin script**,
ʻ U+02BB in oʻ/gʻ, ʼ U+02BC for the apostrophe — never ASCII `'` or `’`).

## Writing: content types (tags are short, one word)

| | post (LinkedIn) | article (long self-published text) | paper (peer-reviewed journal) | section |
|---|---|---|---|---|
| en | Post | Article | Paper | Posts & articles |
| es | Post | Nota | Artículo | Posts, notas y artículos |
| ru | Пост | Заметка | Статья | Посты, заметки и статьи |
| sr | Post | Zapis | Rad | Postovi, zapisi i radovi |
| uz | Post | Qayd | Maqola | Postlar, qaydlar va maqolalar (menu: Nashrlar) |

Conference abstracts (тезисы доклада) are listed with papers under the same filter; their tag is
en Talk abstract, es Ponencia, ru Тезисы, sr Saopštenje, uz Tezis.

Filters are the plurals: es Posts/Notas/Artículos, ru Посты/Заметки/Статьи, sr Postovi/Zapisi/Radovi,
uz Postlar/Qaydlar/Maqolalar.

## Job titles (translated everywhere)

| en | es | ru | sr | uz |
|---|---|---|---|---|
| Principal Software Engineer | Ingeniero de software principal | Главный инженер-программист | Glavni softverski inženjer | Bosh dasturiy taʼminot muhandisi |
| Senior Software Engineer | Ingeniero de software sénior | Старший инженер-программист | Viši softverski inženjer | Katta dasturiy taʼminot muhandisi |
| Software Engineer | Ingeniero de software | Инженер-программист | Softverski inženjer | Dasturiy taʼminot muhandisi |
| Junior Researcher | Investigador júnior | Младший научный сотрудник | Mlađi istraživač | Kichik ilmiy xodim |
| Engineer | Ingeniero | Инженер | Inženjer | Muhandis |
| University Lecturer | Profesor universitario | Преподаватель | Univerzitetski predavač | Universitet oʻqituvchisi |

"Head of Slop Review" (fun role) stays as each language has it now (ru: «Главный ревьюер нейрослопа»).

## Names

- Lomonosov MSU: es «Universidad Estatal de Moscú (MSU)», ru «МГУ имени М. В. Ломоносова» (nbsp between
  initials), sr «MGU „M. V. Lomonosov“», uz «M. V. Lomonosov nomidagi MDU».
- Company, product, library names and code stay as they are (NeoML, ONNX, Boost, CUDA, ABBYY, Huawei…).
- Author: Kirill Golikov / Кирилл Голиков / Kiril Golikov (sr).

## Style

- Translate meaning, not words; keep the author's voice: irony and jokes stay jokes.
- Keep Markdown structure, links, images, code blocks and inline code exactly; never translate code,
  identifiers, URLs, hashtags in `tags`.
- A link to a page in another language than the text gets a mark: [text](url){: hreflang=ru } (shown as a
  small "RU" badge). Linked pages themselves are not translated.
- Inline code that is a human-readable message (a TODO, a printed string) may be translated; identifiers,
  commands and real code may not. Hashtags inside the text are prose and are translated; `tags` are not.
- Spanish addresses readers with **ustedes** (works on every continent), never vosotros.
- Typography of the target language: ru «ёлочки», — with spaces, – without spaces in ranges (2016–2023),
  nbsp after short abbreviations; sr „…“; es «…» or "…" as in the source, inverted ¿¡.

## Other agreed terms

| ru | es | sr | uz | en |
|---|---|---|---|---|
| Аннотация (paper) | Resumen | Apstrakt | Annotatsiya | Abstract |
| ВНЖ / ПМЖ | permiso de residencia / residencia permanente | boravišna dozvola / stalni boravak | yashash uchun ruxsatnoma / doimiy yashash uchun ruxsatnoma | residence permit / permanent residence |
| РУз | Uzbekistán | Uzbekistan | OʻzR | Uzbekistan |
| госуслуги | servicios públicos en línea | e-uprava | davlat xizmatlari | e-government services |

## Projects (`projects/<slug>/<lang>.md`)

| en | es | ru | sr | uz |
|---|---|---|---|---|
| Projects (menu, section; a project's title is its repo name, untranslated) | Proyectos | Проекты | Projekti | Loyihalar |
| Open-source code (home section) | Código abierto | Открытый код | Otvoreni kod | Ochiq kod |
| Library | Biblioteca | Библиотека | Biblioteka | Kutubxona |
| Open-source contributions | Contribuciones de código abierto | Вклад в открытый код | Doprinos otvorenom kodu | Ochiq kodga hissa |
| Storage engine | Motor de almacenamiento | Движок хранения | Mehanizam za skladištenje | Saqlash dvigateli |
| Memory allocator | Asignador de memoria | Аллокатор памяти | Alokator memorije | Xotira allokatori |
| What is inside | Qué incluye | Что внутри | Šta je unutra | Ichida nima bor |
| How it works | Cómo funciona | Как это устроено | Kako radi | Qanday ishlaydi |
| Engineering | Ingeniería | Инженерная часть | Inženjerska strana | Muhandislik |
| Why it matters | Por qué es importante | Почему это важно | Zašto je to važno | Bu nima uchun muhim |
| Limitations | Limitaciones | Ограничения | Ograničenja | Cheklovlar |
| The price, measured | El precio, medido | Цена в цифрах | Izmerena cena | Oʻlchangan narx |
| Self-checks | Autocomprobaciones | Самопроверки | Samoprovere | Oʻz-oʻzini tekshirish |
| Diagnostics | Diagnóstico | Диагностика | Dijagnostika | Diagnostika |
| Technosphere (Mail.Ru Group + MSU) | Technosphere | Техносфера | Tehnosfera | Texnosfera |

Technical terms: pull request stays (ru «пул-реквест», sr «pull request-ovi»); framework — es framework, ru
фреймворк, sr frejmvork, uz freymvork; thread pool — ru «пул потоков», uz «oqimlar puli», es/sr keep "thread
pool"; smart pointer — es puntero inteligente, ru умный указатель, sr pametni pokazivač, uz aqlli koʻrsatkich;
key-value store — es almacén clave-valor, ru хранилище «ключ — значение», sr key-value skladište, uz kalit-qiymat
ombori; waveform — es forma de onda, ru временная диаграмма, sr talasni oblik, uz toʻlqin diagrammasi;
four-state VCD — ru «VCD с четырёхзначной логикой». "The writer's state" is "the internal state" everywhere
(es escritor / sr pisač / uz yozuvchi read as a human writer or a printer). Foreign names in sr take a hyphen
before the ending (README-u, C++-u, ABBYY-ju); in uz the suffix is attached directly (NeoMLga, GitHubdagi).
