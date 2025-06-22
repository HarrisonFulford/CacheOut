import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Terminal as TerminalIcon, Activity, Cpu, HardDrive } from 'lucide-react';

interface TerminalLine {
  id: string;
  timestamp: string;
  type: 'info' | 'success' | 'error' | 'warning' | 'hashrate';
  message: string;
  jobId?: string;
  workerId?: string;
  hashrate?: number;
  cpuUsage?: number;
  memoryUsage?: number;
}

interface TerminalProps {
  jobs: any[];
  className?: string;
}

const Terminal = ({ jobs, className = "" }: TerminalProps) => {
  const [terminalLines, setTerminalLines] = useState<TerminalLine[]>([]);
  const [isConnected, setIsConnected] = useState(true);
  const terminalRef = useRef<HTMLDivElement>(null);

  // Display real job status updates
  useEffect(() => {
    const newLines: TerminalLine[] = [];
    
    jobs.forEach(job => {
      const timestamp = new Date().toLocaleTimeString();
      
      // Add job status updates based on real data
      if (job.status === 'pending') {
        newLines.push({
          id: `${job.job_id}-pending`,
          timestamp,
          type: 'info',
          message: `Job ${job.job_id} queued for execution`,
          jobId: job.job_id
        });
      }
      
      if (job.status === 'running') {
        newLines.push({
          id: `${job.job_id}-running`,
          timestamp,
          type: 'success',
          message: `Job ${job.job_id} started on worker ${job.assigned_worker}`,
          jobId: job.job_id,
          workerId: job.assigned_worker
        });
        
        // Display real job output if available
        if (job.result) {
          newLines.push({
            id: `${job.job_id}-output`,
            timestamp,
            type: 'info',
            message: `Output: ${job.result}`,
            jobId: job.job_id,
            workerId: job.assigned_worker
          });
        }
      }
      
      if (job.status === 'completed') {
        newLines.push({
          id: `${job.job_id}-completed`,
          timestamp,
          type: 'success',
          message: `Job ${job.job_id} completed successfully`,
          jobId: job.job_id,
          workerId: job.assigned_worker
        });
      }
      
      if (job.status === 'failed') {
        newLines.push({
          id: `${job.job_id}-failed`,
          timestamp,
          type: 'error',
          message: `Job ${job.job_id} failed to complete`,
          jobId: job.job_id,
          workerId: job.assigned_worker
        });
      }
    });
    
    if (newLines.length > 0) {
      setTerminalLines(prev => [...prev, ...newLines].slice(-50)); // Keep last 50 lines
    }
  }, [jobs]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalLines]);

  // Set connection status based on whether we have jobs
  useEffect(() => {
    setIsConnected(jobs.length > 0);
  }, [jobs]);

  const getLineColor = (type: TerminalLine['type']) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      case 'hashrate': return 'text-cyan-400';
      default: return 'text-gray-300';
    }
  };

  const getLineIcon = (type: TerminalLine['type']) => {
    switch (type) {
      case 'success': return '✓';
      case 'error': return '✗';
      case 'warning': return '⚠';
      case 'hashrate': return '⚡';
      default: return '>';
    }
  };

  return (
    <Card className={`bg-black/90 backdrop-blur-sm border-green-500/30 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 text-sm">
          <TerminalIcon className="h-4 w-4" />
          Distributed Computing Terminal
          <Badge 
            variant={isConnected ? "default" : "destructive"} 
            className="ml-auto text-xs"
          >
            {isConnected ? "CONNECTED" : "DISCONNECTED"}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div 
          ref={terminalRef}
          className="h-96 bg-black text-green-400 font-mono text-xs p-4 overflow-y-auto"
          style={{ fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace' }}
        >
          {terminalLines.length === 0 ? (
            <div className="text-gray-500">
              <div>Welcome to CacheOut Distributed Computing Terminal</div>
              <div>Waiting for jobs to start...</div>
              <div className="mt-2">
                <div>Available commands:</div>
                <div>• Submit compute job</div>
                <div>• Monitor job status</div>
                <div>• Track resource usage</div>
              </div>
            </div>
          ) : (
            terminalLines.map((line) => (
              <div key={line.id} className="mb-1">
                <span className="text-gray-500">[{line.timestamp}]</span>
                <span className="text-green-500 mx-2">{getLineIcon(line.type)}</span>
                <span className={getLineColor(line.type)}>{line.message}</span>
                {line.hashrate && (
                  <span className="text-cyan-300 ml-2">
                    <Activity className="h-3 w-3 inline mr-1" />
                    {line.hashrate} H/s
                  </span>
                )}
                {line.cpuUsage && (
                  <span className="text-blue-300 ml-2">
                    <Cpu className="h-3 w-3 inline mr-1" />
                    {line.cpuUsage}%
                  </span>
                )}
                {line.memoryUsage && (
                  <span className="text-purple-300 ml-2">
                    <HardDrive className="h-3 w-3 inline mr-1" />
                    {line.memoryUsage}%
                  </span>
                )}
              </div>
            ))
          )}
          <div className="text-green-500 animate-pulse">
            <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span>
            <span className="text-green-500 mx-2">{'>'}</span>
            <span className="text-green-400">_</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default Terminal; 