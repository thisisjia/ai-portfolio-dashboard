'use client';

import { useState, useEffect } from 'react';
import { api, SQLQuery, SQLResult } from '@/lib/api';

export default function SQLDemo() {
  const [queries, setQueries] = useState<SQLQuery[]>([]);
  const [selectedQuery, setSelectedQuery] = useState<string>('');
  const [result, setResult] = useState<SQLResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQueries();
  }, []);

  const loadQueries = async () => {
    try {
      const data = await api.getSQLQueries();
      setQueries(data);
    } catch (err) {
      console.error('Failed to load queries:', err);
      setError('Failed to load queries');
    }
  };

  const executeQuery = async () => {
    if (!selectedQuery) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const data = await api.executeSQLQuery(selectedQuery);
      setResult(data);
    } catch (err) {
      console.error('Failed to execute query:', err);
      setError('Failed to execute query');
    } finally {
      setIsLoading(false);
    }
  };

  const highlightSQL = (sql: string) => {
    const keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'LIMIT', 'JOIN', 'AS', 'COUNT', 'AVG', 'DESC'];
    let highlighted = sql;
    
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      highlighted = highlighted.replace(regex, `<span class="text-pink-500 font-semibold">${keyword}</span>`);
    });
    
    return highlighted;
  };

  return (
    <div className="space-y-6">
      {/* Query Selector */}
      <div className="flex gap-4">
        <select
          value={selectedQuery}
          onChange={(e) => setSelectedQuery(e.target.value)}
          className="flex-1 max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select a query to execute...</option>
          {queries.map((query) => (
            <option key={query.name} value={query.name}>
              {query.name}
            </option>
          ))}
        </select>
        <button
          onClick={executeQuery}
          disabled={!selectedQuery || isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Execute Query
        </button>
      </div>

      {/* Query Description */}
      {selectedQuery && (
        <p className="text-gray-600">
          {queries.find(q => q.name === selectedQuery)?.description}
        </p>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-gray-600">Executing query...</p>
        </div>
      )}

      {/* Results */}
      {result && !isLoading && (
        <div className="space-y-4">
          {/* SQL Display */}
          <div className="bg-gray-900 text-gray-300 p-4 rounded-lg overflow-x-auto">
            <pre className="text-sm">
              <code dangerouslySetInnerHTML={{ __html: highlightSQL(result.sql) }} />
            </pre>
          </div>

          {/* Results Table */}
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {result.columns.map((column) => (
                      <th
                        key={column}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {result.rows.map((row, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      {result.columns.map((column) => (
                        <td key={column} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {typeof row[column] === 'string' && (row[column].startsWith('[') || row[column].startsWith('{'))
                            ? JSON.parse(row[column]).join(', ')
                            : row[column] ?? '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-6 py-3 bg-gray-50 text-sm text-gray-600">
              Returned {result.row_count} row(s)
            </div>
          </div>
        </div>
      )}
    </div>
  );
}