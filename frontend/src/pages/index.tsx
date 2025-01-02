import { TokenAnalysis } from '../components/TokenAnalysis';
import { Logo } from '../components/Logo';

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center mb-10">
          <Logo />
          <h2 className="text-3xl font-bold text-gray-900 ml-5">
            Ludo Token Analysis Tool
          </h2>
        </div>
        <TokenAnalysis />
      </div>
    </main>
  );
} 