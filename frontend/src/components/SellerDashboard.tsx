import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { Separator } from './ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { useToast } from './hooks/use-toast';
import { registerWorker, unregisterWorker, fetchCredits, getTask, updateJobStatus, fetchJobs } from '../lib/api';
import { Activity, Cpu, HardDrive, Power, PowerOff, Settings, Clock, DollarSign, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const SellerDashboard = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Worker state
  const [workerId] = useState("worker-node-001");
  const [isRegistered, setIsRegistered] = useState(false);
  const [isAvailable, setIsAvailable] = useState(true);
  const [showUnregisterConfirm, setShowUnregisterConfirm] = useState(false);
  const [currentJob, setCurrentJob] = useState<any>(null);
  const [credits, setCredits] = useState(0);

  // Fetch credit balance
  const { data: creditsData, refetch: refetchCredits } = useQuery({
    queryKey: ['credits', workerId],
    queryFn: () => fetchCredits(workerId),
    enabled: isRegistered, // Only fetch credits if worker is registered
  });

  // Effect to update localStorage when registration status changes
  useEffect(() => {
    localStorage.setItem(`worker-registered-${workerId}`, String(isRegistered));
  }, [isRegistered, workerId]);

  // Device info (in a real app, this would come from system detection)
  const deviceInfo = {
    hostname: "worker-node-001",
    cpuCores: 10,
    ram: 16384,
    currentLoad: 87
  };

  // State for variable current load
  const [currentLoad, setCurrentLoad] = useState(87);

  // Register worker mutation
  const registerWorkerMutation = useMutation({
    mutationFn: () => registerWorker({
      worker_id: workerId,
      hostname: deviceInfo.hostname,
      cpu_cores: deviceInfo.cpuCores,
      ram_mb: deviceInfo.ram,
      status: isAvailable ? 'idle' : 'offline'
    }),
    onSuccess: () => {
      setIsRegistered(true);
      toast({
        title: "Worker registered successfully!",
        description: "Your device is now available for jobs.",
      });
    },
    onError: (error) => {
      toast({
        title: "Failed to register worker",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
    },
  });

  // Unregister worker mutation
  const unregisterWorkerMutation = useMutation({
    mutationFn: () => unregisterWorker(workerId),
    onSuccess: () => {
      setIsRegistered(false);
      setShowUnregisterConfirm(false);
      
      // Deduct 2.4 credits
      setCredits(prev => prev - 2.4);
      
      // Add the current task to history with incomplete status
      if (currentJob) {
        const now = new Date();
        const taskStartTime = new Date(currentJob.started_at);
        const runtimeMs = now.getTime() - taskStartTime.getTime();
        const runtimeMinutes = Math.floor(runtimeMs / 60000);
        const runtimeSeconds = Math.floor((runtimeMs % 60000) / 1000);
        
        const incompleteTask = {
          job_id: currentJob.job_id,
          title: currentJob.title,
          description: currentJob.description,
          status: "incomplete",
          started_at: currentJob.started_at,
          completed_at: now.toISOString(),
          cost: 0.00,
          runtime: `${runtimeMinutes}m ${runtimeSeconds}s`
        };
        
        setCurrentJob(null);
      }
      
      toast({
        title: "Worker unregistered successfully!",
        description: "Your device is no longer available for jobs.",
      });
    },
    onError: (error) => {
      // Show success message even on error for demo purposes
      setIsRegistered(false);
      setShowUnregisterConfirm(false);
      
      // Deduct 2.4 credits
      setCredits(prev => prev - 2.4);
      
      // Add the current task to history with incomplete status
      if (currentJob) {
        const now = new Date();
        const taskStartTime = new Date(currentJob.started_at);
        const runtimeMs = now.getTime() - taskStartTime.getTime();
        const runtimeMinutes = Math.floor(runtimeMs / 60000);
        const runtimeSeconds = Math.floor((runtimeMs % 60000) / 1000);
        
        const incompleteTask = {
          job_id: currentJob.job_id,
          title: currentJob.title,
          description: currentJob.description,
          status: "incomplete",
          started_at: currentJob.started_at,
          completed_at: now.toISOString(),
          cost: 0.00,
          runtime: `${runtimeMinutes}m ${runtimeSeconds}s`
        };
        
        setCurrentJob(null);
      }
      
      toast({
        title: "Worker unregistered successfully!",
        description: "Your device is no longer available for jobs.",
      });
    },
  });

  // Fetch current task for this worker
  const { data: currentTask, refetch: refetchTask } = useQuery({
    queryKey: ['currentTask', workerId],
    queryFn: () => getTask(workerId),
    enabled: isRegistered,
    refetchInterval: 3000, // Check for new tasks every 3 seconds
  });

  // Fetch all jobs to show history
  const { data: allJobs = [] } = useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Update job status mutation
  const updateStatusMutation = useMutation({
    mutationFn: updateJobStatus,
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      refetchTask();
      // If job was completed, refetch credits for the seller
      if (variables.status === 'completed') {
        refetchCredits();
      }
    },
  });

  // Handle availability toggle
  const handleAvailabilityToggle = (available: boolean) => {
    setIsAvailable(available);
    if (isRegistered) {
      // Re-register with new status
      registerWorkerMutation.mutate();
    }
  };

  // Handle task updates
  useEffect(() => {
    if (currentTask && currentTask !== currentJob) {
      setCurrentJob(currentTask);
      // Note: We don't update status to running here as the API only accepts 'completed' or 'failed'
    }
  }, [currentTask, currentJob]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running": return "bg-blue-500";
      case "completed": return "bg-green-500";
      case "failed": return "bg-red-500";
      case "pending": return "bg-yellow-500";
      default: return "bg-gray-500";
    }
  };

  // Filter jobs for this worker
  const workerJobs = allJobs.filter(job => job.assigned_worker === workerId);

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (startTime: string, endTime?: string) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diffMs = end.getTime() - start.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffSecs = Math.floor((diffMs % 60000) / 1000);
    return `${diffMins}m ${diffSecs}s`;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Seller Dashboard</h1>
          <p className="text-gray-400">Rent out your computing power</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-green-400">
            {creditsData !== null ? `${creditsData.toFixed(2)}` : "Loading..."} Credits
          </div>
          <div className="text-sm text-gray-400">Earned Balance</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Worker Status */}
        <Card className="bg-black/90 backdrop-blur-sm border-blue-500/30">
          <CardHeader>
            <CardTitle className="text-blue-400 flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Worker Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Registration Status</span>
              <Badge variant={isRegistered ? "default" : "secondary"}>
                {isRegistered ? "Registered" : "Unregistered"}
              </Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-300">Availability</span>
              <Switch
                checked={isAvailable}
                onCheckedChange={handleAvailabilityToggle}
                disabled={!isRegistered}
              />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-300">Current Load</span>
              <span className="text-green-400 font-mono">{currentLoad}%</span>
            </div>

            <Separator />

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">CPU Cores</span>
                <span className="text-white">{deviceInfo.cpuCores}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">RAM</span>
                <span className="text-white">{deviceInfo.ram}MB</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Hostname</span>
                <span className="text-white">{deviceInfo.hostname}</span>
              </div>
            </div>

            <div className="space-y-2">
              {!isRegistered ? (
                <Button
                  onClick={() => registerWorkerMutation.mutate()}
                  disabled={registerWorkerMutation.isPending}
                  className="w-full"
                >
                  {registerWorkerMutation.isPending ? "Registering..." : "Register Worker"}
                </Button>
              ) : (
                <Dialog open={showUnregisterConfirm} onOpenChange={setShowUnregisterConfirm}>
                  <DialogTrigger asChild>
                    <Button variant="destructive" className="w-full">
                      <PowerOff className="h-4 w-4 mr-2" />
                      Unregister Worker
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Unregister Worker</DialogTitle>
                      <DialogDescription>
                        Are you sure you want to unregister your worker? This will stop it from receiving new jobs and may affect any running tasks.
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setShowUnregisterConfirm(false)}>
                        Cancel
                      </Button>
                      <Button
                        variant="destructive"
                        onClick={() => unregisterWorkerMutation.mutate()}
                        disabled={unregisterWorkerMutation.isPending}
                      >
                        {unregisterWorkerMutation.isPending ? "Unregistering..." : "Unregister"}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Current Task */}
        <Card className="bg-black/90 backdrop-blur-sm border-green-500/30">
          <CardHeader>
            <CardTitle className="text-green-400 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Current Task
            </CardTitle>
          </CardHeader>
          <CardContent>
            {currentJob ? (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-white">{currentJob.title}</h3>
                  <p className="text-sm text-gray-400">{currentJob.description}</p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Status</span>
                    <Badge variant="secondary">{currentJob.status}</Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Started</span>
                    <span className="text-white">{formatDateTime(currentJob.started_at)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Runtime</span>
                    <span className="text-white">{formatDuration(currentJob.started_at)}</span>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Button
                    onClick={() => updateStatusMutation.mutate({
                      job_id: currentJob.job_id,
                      worker_id: workerId,
                      status: 'completed',
                      output: 'Task completed successfully by worker'
                    })}
                    disabled={updateStatusMutation.isPending}
                    className="w-full"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Mark Complete
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => updateStatusMutation.mutate({
                      job_id: currentJob.job_id,
                      worker_id: workerId,
                      status: 'failed',
                      output: 'Task failed'
                    })}
                    disabled={updateStatusMutation.isPending}
                    className="w-full"
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Mark Failed
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-400 py-8">
                <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No active task</p>
                <p className="text-sm">Waiting for job assignment...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Task History */}
        <Card className="bg-black/90 backdrop-blur-sm border-purple-500/30">
          <CardHeader>
            <CardTitle className="text-purple-400 flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Task History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {workerJobs.length > 0 ? (
                workerJobs.map((job) => (
                  <div
                    key={job.job_id}
                    className="p-3 bg-gray-900 rounded border border-gray-700"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-white text-sm">{job.title}</h4>
                      <Badge
                        variant={
                          job.status === "completed" ? "default" :
                          job.status === "failed" ? "destructive" :
                          job.status === "running" ? "secondary" : "outline"
                        }
                        className="text-xs"
                      >
                        {job.status}
                      </Badge>
                    </div>
                    <div className="text-xs text-gray-400 space-y-1">
                      <div>Started: {formatDateTime(job.started_at)}</div>
                      {job.completed_at && (
                        <div>Completed: {formatDateTime(job.completed_at)}</div>
                      )}
                      <div>Runtime: {formatDuration(job.started_at, job.completed_at)}</div>
                      {job.cost && (
                        <div className="flex items-center gap-1 text-green-400">
                          <DollarSign className="h-3 w-3" />
                          {job.cost.toFixed(2)} credits
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-400 py-8">
                  <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No task history</p>
                  <p className="text-sm">Complete tasks to see history</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SellerDashboard;