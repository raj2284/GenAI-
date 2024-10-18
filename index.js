const express = require('express');
const { exec } = require('child_process');
const bodyParser = require('body-parser');
const path = require('path');
const session = require('express-session');
const app = express();
const PORT = 3000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Set up session middleware
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false } 
}));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static("views"));
app.get('/', (req, res) => {
    res.render('index');
});

app.post('/generate', (req, res) => {
    const { youtubeLink, quizNo } = req.body;
    console.log('Request received:', { youtubeLink, quizNo });

    if (!youtubeLink || !quizNo) {
        return res.status(400).json({ error: 'youtubeLink and quizNo are required' });
    }

    const parsedQuizNo = parseInt(quizNo);
    if (isNaN(parsedQuizNo) || parsedQuizNo <= 0 || parsedQuizNo > 50) {
        return res.status(400).json({ error: 'quizNo must be a positive integer between 1 and 50.' });
    }

    const escapedLink = youtubeLink.replace(/"/g, '\\"');
    console.log(`Escaped link: ${escapedLink}`);

    const command = `python ./temp.py "${escapedLink}" ${parsedQuizNo}`;
    console.log(`Executing command: ${command}`);

    // Execute the command
    exec(command, { timeout: 60000 }, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing script: ${error.message}`);
            return res.status(500).json({ error: 'Internal Server Error' });
        }

        if (stderr) {
            console.error(`Script error: ${stderr}`);
            return res.status(500).json({ error: 'Script execution error' });
        }

        try {
            const jsonResponse = JSON.parse(stdout);

            if (jsonResponse.error) {
                return res.status(500).json({ error: jsonResponse.error });
            }

            // Store the quiz data in the session
            req.session.quizData = {
                youtube_link: youtubeLink,
                quiz_number: parsedQuizNo,
                summary: jsonResponse.summary,
                quiz: jsonResponse.quiz
            };
            // console.log('Quiz data:', req.session.quizData);

            return res.render('result', req.session.quizData);
        } catch (parseError) {
            console.error('Failed to parse response from Python script:', parseError);
            return res.status(500).json({ error: 'Failed to parse response from Python script' });
        }
    });
});

app.get('/take-quiz', (req, res) => {
    if (!req.session.quizData) {
        return res.redirect('/');
    }
    console.log('Quiz data:', req.session.quizData.quiz);

    res.render('quiz', { quiz: req.session.quizData.quiz });
});


// Handle 404 errors
app.use((req, res) => {
    res.status(404).send('Not Found');
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}/`);
});










// const response = {

//     "summary": {
//         "topic1": "topic1 summary",
//         "topic2": "topic2 summary",
//         "topic3": "topic3 summary",
//         "topic4": "topic4 summary",
//     },
//     "quiz": [
//         {
//             question: 'Why was M. Hamel dressed in his formal attire on the day of the last lesson?',
//             options: [
//                 'A. He was going to a wedding',
//                 'B. He was going to a funeral',
//                 'C. It was a special occasion, the last French lesson',
//                 'D. He was going to a party'
//             ],
//             answer: 'C. It was a special occasion, the last French lesson'
//         },
//         {
//             question: 'What was the order from Berlin that was announced in the classroom?',
//             options: [
//                 'A. To teach only French in the schools of Alsace and Lorraine',
//                 'B. To teach only German in the schools of Alsace and Lorraine',
//                 'C. To close all schools in Alsace and Lorraine',
//                 'D. To open new schools in Alsace and Lorraine'
//             ],
//             answer: 'B. To teach only German in the schools of Alsace and Lorraine'
//         },
//         {
//             question: "How did the students feel after hearing M. Hamel's speech?",
//             options: [
//                 'A. They felt happy and excited',
//                 'B. They felt sad and regretful',
//                 'C. They felt angry and frustrated',
//                 'D. They felt indifferent and uninterested'
//             ],
//             answer: 'B. They felt sad and regretful'
//         }]

// }