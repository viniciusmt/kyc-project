'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/services/auth';

export default function Header() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [user, setUser] = useState<{ email?: string } | null>(null);

  useEffect(() => {
    setMounted(true);
    setCompanyName(authService.getCompanyName() || '');
    setUser(authService.getCurrentUser());
  }, []);

  const handleLogout = () => {
    authService.logout();
    router.push('/');
  };

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Company */}
          <div className="flex items-center">
            <Link href="/dashboard" className="text-xl font-bold text-primary">
              🔍 KYC System
            </Link>
            <div className="ml-6 text-sm text-gray-600">
              <span className="font-medium">{mounted ? companyName : ''}</span>
              <span className="mx-2">•</span>
              <span>{mounted ? user?.email : ''}</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <Link
              href="/dashboard"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              🔍 Dossiês
            </Link>
            <Link
              href="/monitoring"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              📊 Monitoramento
            </Link>
            <button
              onClick={handleLogout}
              className="px-3 py-2 rounded-md text-sm font-medium text-red-600 hover:bg-red-50"
            >
              🚪 Sair
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
