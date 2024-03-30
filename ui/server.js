import express, { static as serveStatic } from 'express';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import cors from 'cors';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3000;

app.use(cors({
    origin: 'https://phh.internal',
}))

// Middleware to serve static files

app.use('/assets', serveStatic('dist/assets'));
app.use('/vite.svg', serveStatic('dist/vite.svg'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/dist/index.html');
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
