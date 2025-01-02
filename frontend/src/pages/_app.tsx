import '../styles/globals.css';
import type { AppProps } from 'next/app';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <h1 className="text-xl font-semibold text-gray-800">Token Analysis Tool</h1>
        </div>
      </nav>
      <Component {...pageProps} />
    </div>
  );
}

export default MyApp; 