'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  isDark?: boolean;
}

export default function MarkdownRenderer({
  content,
  className = "",
  isDark = false
}: MarkdownRendererProps) {
  const baseClasses = isDark ? "prose prose-invert" : "prose";
  const proseClasses = `${baseClasses} prose-sm max-w-none ${className}`;

  return (
    <div className={proseClasses}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className={`text-2xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className={`text-xl font-bold mb-3 mt-6 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className={`text-lg font-semibold mb-2 mt-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {children}
            </h3>
          ),
          p: ({ children }) => (
            <p className={`mb-4 leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {children}
            </p>
          ),
          ul: ({ children }) => (
            <ul className={`list-disc list-inside mb-4 space-y-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className={`list-decimal list-inside mb-4 space-y-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="ml-2">{children}</li>
          ),
          strong: ({ children }) => (
            <strong className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic">{children}</em>
          ),
          code: ({ node, inline, className, children, ...props }: any) =>
            inline ? (
              <code className={`px-1 py-0.5 rounded text-sm font-mono ${
                isDark ? 'bg-gray-800 text-blue-400' : 'bg-gray-100 text-blue-600'
              }`}>
                {children}
              </code>
            ) : (
              <code className={`block p-3 rounded-lg text-sm font-mono overflow-x-auto ${
                isDark ? 'bg-gray-900 text-gray-300' : 'bg-gray-50 text-gray-800'
              }`}>
                {children}
              </code>
            ),
          pre: ({ children }) => (
            <pre className={`p-3 rounded-lg overflow-x-auto text-sm ${
              isDark ? 'bg-gray-900 text-gray-300' : 'bg-gray-50 text-gray-800'
            }`}>
              {children}
            </pre>
          ),
          blockquote: ({ children }) => (
            <blockquote className={`border-l-4 pl-4 italic ${
              isDark ? 'border-blue-500 text-gray-300' : 'border-blue-500 text-gray-600'
            }`}>
              {children}
            </blockquote>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              className={`underline hover:no-underline ${
                isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700'
              }`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}