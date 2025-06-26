# Health & Fitness Chatbot Widget

A modern, embeddable chatbot widget that connects to your AI Health & Fitness backend. The widget appears as a floating button in the bottom-right corner of your website and expands into a full chat interface when clicked.

## Features

- 🎯 Modern, floating design
- 🌟 Smooth animations
- 📱 Fully responsive
- 🎨 Customizable theme
- 🔌 Easy integration
- 🤖 AI-powered responses

## Installation

1. Download the built files from the `dist` directory:
   - `health-fitness-chatbot.es.js` (ES Module version)
   - `health-fitness-chatbot.umd.js` (UMD version)

2. Add the required dependencies to your HTML:
```html
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
```

3. Add the chatbot script:
```html
<script src="path/to/health-fitness-chatbot.umd.js"></script>
```

## Usage

1. Add a container div where you want the chatbot to appear:
```html
<div id="health-fitness-chatbot"></div>
```

2. Initialize the chatbot:
```html
<script>
  HealthFitnessChatbot.mount('health-fitness-chatbot', {
    apiUrl: 'http://your-backend-url/chat'
  });
</script>
```

## Configuration Options

The `mount` function accepts the following configuration options:

```javascript
{
  // The URL of your backend API (required)
  apiUrl: 'http://your-backend-url/chat',
  
  // Additional options can be added here in future versions
}
```

## Development

1. Clone the repository
2. Install dependencies:
```bash
pnpm install
```

3. Start the development server:
```bash
pnpm run dev
```

4. Build for production:
```bash
pnpm run build
```

## Backend API Requirements

The backend API should:

1. Accept POST requests at the specified endpoint
2. Expect JSON data in the format:
```json
{
  "message": "User's message here"
}
```

3. Return JSON responses in the format:
```json
{
  "response": "AI assistant's response here"
}
```

## Browser Support

The widget supports all modern browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT License 