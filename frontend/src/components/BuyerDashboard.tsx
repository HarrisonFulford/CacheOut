import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { Separator } from './ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useToast } from './hooks/use-toast';
import { fetchJobs, fetchCredits, submitJob, processNaturalLanguage, JobSubmission } from '../lib/api';
import { FileText, Play, MessageSquare, Upload, Download, Activity, Cpu, HardDrive, Terminal as TerminalIcon } from 'lucide-react';
import Terminal from './Terminal';

// Get buyer ID from environment or use a default
const BUYER_ID = import.meta.env.VITE_BUYER_ID || "sample-buyer";

const TerminalComponent = ({ jobs }: { jobs: Job[] }) => {
  const [expandedJobs, setExpandedJobs] = useState<Set<string>>(new Set());

  const toggleJobVisibility = (jobId: string) => {
    const newExpanded = new Set(expandedJobs);
    if (newExpanded.has(jobId)) {
      newExpanded.delete(jobId);
    } else {
      newExpanded.add(jobId);
    }
    setExpandedJobs(newExpanded);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running": return "bg-blue-500";
      case "completed": return "bg-green-500";
      case "failed": return "bg-red-500";
      case "pending": return "bg-yellow-500";
      default: return "bg-gray-500";
    }
  };

  return (
    <Card className="bg-black/90 backdrop-blur-sm border-green-500/30">
      <CardHeader className="pb-3">
        <CardTitle className="text-green-400 flex items-center gap-2 text-sm">
          <TerminalIcon className="h-4 w-4" />
          Job Terminal
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="h-96 bg-black text-green-400 font-mono text-xs p-4 overflow-y-auto">
          {jobs.length === 0 ? (
            <div className="text-gray-500">
              <div>No jobs submitted yet...</div>
              <div>Submit a job to see terminal output</div>
            </div>
          ) : (
            jobs.map((job) => (
              <div key={job.job_id} className="mb-4">
                <div 
                  className="flex items-center gap-2 cursor-pointer hover:text-green-300"
                  onClick={() => toggleJobVisibility(job.job_id)}
                >
                  <span className={`w-2 h-2 rounded-full ${getStatusColor(job.status)}`}></span>
                  <span className="text-green-400">{job.job_id}</span>
                  <span className="text-gray-500">-</span>
                  <span className="text-white">{job.title}</span>
                  <span className="text-gray-500">({job.status})</span>
                </div>
                
                {expandedJobs.has(job.job_id) && (
                  <div className="ml-4 mt-2 p-2 bg-gray-900 rounded border border-gray-700">
                    <div className="text-gray-400 mb-2">Job Details:</div>
                    <div className="text-sm">
                      <div>Status: <span className="text-green-400">{job.status}</span></div>
                      <div>Worker: <span className="text-blue-400">{job.assigned_worker || 'Unassigned'}</span></div>
                      <div>Created: <span className="text-yellow-400">{new Date(job.created_at).toLocaleString()}</span></div>
                      {job.started_at && (
                        <div>Started: <span className="text-yellow-400">{new Date(job.started_at).toLocaleString()}</span></div>
                      )}
                      {job.completed_at && (
                        <div>Completed: <span className="text-yellow-400">{new Date(job.completed_at).toLocaleString()}</span></div>
                      )}
                      {job.result && (
                        <div className="mt-2">
                          <div className="text-gray-400 mb-1">Output:</div>
                          <pre className="text-xs bg-gray-800 p-2 rounded overflow-x-auto">{job.result}</pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

const BuyerDashboard = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Form state
  const [jobName, setJobName] = useState("");
  const [jobType, setJobType] = useState("Custom");
  const [command, setCommand] = useState("");
  const [naturalLanguagePrompt, setNaturalLanguagePrompt] = useState("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [cpuCores, setCpuCores] = useState([4]);
  const [ram, setRam] = useState([8192]);
  const [priority, setPriority] = useState("medium");
  const [duration, setDuration] = useState("30");
  const [generatedScript, setGeneratedScript] = useState("");
  const [scriptExplanation, setScriptExplanation] = useState("");
  const [showGeneratedScript, setShowGeneratedScript] = useState(false);
  const [isProcessingAI, setIsProcessingAI] = useState(false);
  const [jobRunning, setJobRunning] = useState(false);

  // Fetch credit balance
  const { data: credits, refetch: refetchCredits } = useQuery({
    queryKey: ['credits', BUYER_ID],
    queryFn: () => fetchCredits(BUYER_ID),
  });

  // Fetch jobs with auto-refresh
  const { data: fetchedJobs, refetch: refetchJobs } = useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    refetchInterval: 2000, // Poll every 2 seconds
  });

  // Submit job mutation
  const submitJobMutation = useMutation({
    mutationFn: (jobData: JobSubmission) => submitJob(jobData, import.meta.env.VITE_ADMIN_TOKEN || ""),
    onSuccess: () => {
      toast({
        title: "Job submitted successfully!",
        description: "Your job has been added to the queue.",
      });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      refetchCredits();
      // Reset form
      setJobName("");
      setJobType("Custom");
      setCommand("");
      setNaturalLanguagePrompt("");
      setUploadedFile(null);
      setCpuCores([4]);
      setRam([8192]);
      setPriority("medium");
      setDuration("30");
      setGeneratedScript("");
      setScriptExplanation("");
      setShowGeneratedScript(true);
      setJobRunning(true);
    },
    onError: (error) => {
      toast({
        title: "Failed to submit job",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
    },
  });

  // Handle job type change
  const handleJobTypeChange = (newJobType: string) => {
    setJobType(newJobType);
    setCommand("");
    setNaturalLanguagePrompt("");
    setUploadedFile(null);
    setGeneratedScript("");
    setScriptExplanation("");
    setShowGeneratedScript(false);
    
    if (newJobType === "Natural Language") {
      setCpuCores([6]);
      setRam([16384]);
      setDuration("45");
    } else {
      setCpuCores([4]);
      setRam([8192]);
      setDuration("");
    }
  };

  // Handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setCommand(content);
      };
      reader.readAsText(file);
    }
  };

  // Process natural language with Gemini API
  const handleNaturalLanguageProcess = async () => {
    if (!naturalLanguagePrompt.trim()) {
      toast({
        title: "Missing prompt",
        description: "Please enter a description of what you want to do.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessingAI(true);
    try {
      const result = await processNaturalLanguage(naturalLanguagePrompt, import.meta.env.VITE_ADMIN_TOKEN || "");
      
      setGeneratedScript(result.script);
      setScriptExplanation(result.explanation);
      setCpuCores([result.estimatedCores]);
      setRam([result.estimatedRam]);
      setDuration(result.estimatedDuration.toString());
      setCommand(result.script);
      setShowGeneratedScript(true);
      
      toast({
        title: "AI Processing Complete!",
        description: "Script generated and resource requirements estimated.",
      });
    } catch (error) {
      toast({
        title: "Failed to process natural language",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
    } finally {
      setIsProcessingAI(false);
    }
  };

  // Handle Enter key in natural language textarea
  const handleNaturalLanguageKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleNaturalLanguageProcess();
    }
  };

  // Download generated script
  const downloadGeneratedScript = () => {
    if (!generatedScript) return;
    
    const blob = new Blob([generatedScript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated_script_${Date.now()}.sh`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Script Downloaded",
      description: "Generated script has been saved to your computer.",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running": return "bg-blue-500";
      case "completed": return "bg-green-500";
      case "failed": return "bg-red-500";
      case "pending": return "bg-yellow-500";
      default: return "bg-gray-500";
    }
  };

  const getJobIcon = (type: string) => {
    switch (type) {
      case "Custom": return <FileText className="h-4 w-4" />;
      case "Natural Language": return <MessageSquare className="h-4 w-4" />;
      default: return <Play className="h-4 w-4" />;
    }
  };

  const handleSubmitJob = async (e: React.MouseEvent) => {
    e.preventDefault();
    
    let finalCommand = command;
    let finalCpuCores = cpuCores[0];
    let finalRam = ram[0];
    let finalDuration = duration;

    if (!finalCommand.trim()) {
      toast({
        title: "Missing command",
        description: "Please enter a command to execute or upload a script.",
        variant: "destructive",
      });
      return;
    }

    const priorityMap: Record<string, number> = {
      "high": 1,
      "medium": 3,
      "low": 5
    };

    const jobData: JobSubmission = {
      title: jobName || "Unnamed Job",
      description: `Job type: ${jobType || "Unknown"}`,
      code: finalCommand,
      priority: priorityMap[priority] || 3,
      required_cores: finalCpuCores,
      required_ram_mb: finalRam,
      command: finalCommand,
      parameters: JSON.stringify({
        job_name: jobName,
        job_type: jobType,
        estimated_duration: finalDuration,
        natural_language_prompt: naturalLanguagePrompt || undefined
      }),
      buyer_id: BUYER_ID
    };

    submitJobMutation.mutate(jobData, {
      onSuccess: () => {
        setJobRunning(true);
        const jobCost = ((cpuCores[0] * 0.1) + (ram[0] / 1024 * 0.05) + 1.0);
        if (credits !== null) {
          toast({
            title: "Job submitted successfully!",
            description: `Job cost: ${jobCost.toFixed(2)} credits. Remaining: ${(credits - jobCost).toFixed(2)} credits.`,
          });
        }
      },
    });
  };

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
          <h1 className="text-3xl font-bold text-white">Buyer Dashboard</h1>
          <p className="text-gray-400">Submit and monitor compute jobs</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-green-400">
            {credits !== null ? `${credits.toFixed(2)}` : "Loading..."} Credits
          </div>
          <div className="text-sm text-gray-400">Available Balance</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Job Submission Form */}
        <Card className="bg-black/90 backdrop-blur-sm border-blue-500/30">
          <CardHeader>
            <CardTitle className="text-blue-400">Submit New Job</CardTitle>
            <CardDescription>Create and submit a compute job</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="jobName">Job Name</Label>
              <Input
                id="jobName"
                placeholder="Enter job name"
                value={jobName}
                onChange={(e) => setJobName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>Job Type</Label>
              <Select value={jobType} onValueChange={handleJobTypeChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Custom">Custom Script</SelectItem>
                  <SelectItem value="Natural Language">Natural Language</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {jobType === "Natural Language" ? (
              <div className="space-y-2">
                <Label>Describe what you want to do</Label>
                <Textarea
                  placeholder="e.g., 'Mine cryptocurrency using CPU', 'Process large dataset', 'Train machine learning model'"
                  value={naturalLanguagePrompt}
                  onChange={(e) => setNaturalLanguagePrompt(e.target.value)}
                  onKeyDown={handleNaturalLanguageKeyPress}
                  rows={3}
                />
                <Button
                  onClick={handleNaturalLanguageProcess}
                  disabled={isProcessingAI || !naturalLanguagePrompt.trim()}
                  className="w-full"
                >
                  {isProcessingAI ? "Processing..." : "Generate Script"}
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                <Label>Command or Script</Label>
                <Textarea
                  placeholder="Enter your command or script here..."
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  rows={4}
                />
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => document.getElementById('fileUpload')?.click()}
                    className="flex-1"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Script
                  </Button>
                  <input
                    id="fileUpload"
                    type="file"
                    accept=".sh,.py,.js,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>
              </div>
            )}

            {showGeneratedScript && generatedScript && (
              <div className="space-y-2">
                <Label>Generated Script</Label>
                <div className="bg-gray-900 p-3 rounded border border-gray-700">
                  <pre className="text-xs text-green-400 overflow-x-auto">{generatedScript}</pre>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={downloadGeneratedScript}
                    className="flex-1"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
                {scriptExplanation && (
                  <div className="text-sm text-gray-400 mt-2">
                    <strong>Explanation:</strong> {scriptExplanation}
                  </div>
                )}
              </div>
            )}

            <Separator />

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>CPU Cores: {cpuCores[0]}</Label>
                <Slider
                  value={cpuCores}
                  onValueChange={setCpuCores}
                  max={16}
                  min={1}
                  step={1}
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label>RAM: {ram[0]}MB</Label>
                <Slider
                  value={ram}
                  onValueChange={setRam}
                  max={32768}
                  min={1024}
                  step={1024}
                  className="w-full"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Priority</Label>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Duration (minutes)</Label>
                <Input
                  type="number"
                  placeholder="30"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                />
              </div>
            </div>

            <Button
              onClick={handleSubmitJob}
              disabled={submitJobMutation.isPending || !command.trim()}
              className="w-full"
            >
              {submitJobMutation.isPending ? "Submitting..." : "Submit Job"}
            </Button>
          </CardContent>
        </Card>

        {/* Job History */}
        <Card className="bg-black/90 backdrop-blur-sm border-purple-500/30">
          <CardHeader>
            <CardTitle className="text-purple-400">Job History</CardTitle>
            <CardDescription>Monitor your submitted jobs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {fetchedJobs && fetchedJobs.length > 0 ? (
                fetchedJobs
                  .filter(job => job.buyer_id === BUYER_ID)
                  .map((job) => (
                    <div
                      key={job.job_id}
                      className="flex items-center justify-between p-3 bg-gray-900 rounded border border-gray-700"
                    >
                      <div className="flex items-center gap-3">
                        {getJobIcon(jobType)}
                        <div>
                          <div className="font-medium text-white">{job.title}</div>
                          <div className="text-sm text-gray-400">
                            {formatDateTime(job.created_at)}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={
                            job.status === "completed" ? "default" :
                            job.status === "failed" ? "destructive" :
                            job.status === "running" ? "secondary" : "outline"
                          }
                        >
                          {job.status}
                        </Badge>
                        <div className="text-sm text-gray-400">
                          {job.started_at ? formatDuration(job.started_at, job.completed_at) : "-"}
                        </div>
                      </div>
                    </div>
                  ))
              ) : (
                <div className="text-center text-gray-400 py-8">
                  No jobs submitted yet
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Terminal Component */}
      {fetchedJobs && fetchedJobs.length > 0 && (
        <TerminalComponent jobs={fetchedJobs.filter(job => job.buyer_id === BUYER_ID)} />
      )}
    </div>
  );
};

export default BuyerDashboard;
