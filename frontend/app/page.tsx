import { useState } from "react";
import axios from "axios";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";

export default function RepoAnalysis() {
  const [repoUrl, setRepoUrl] = useState("");
  const [repoId, setRepoId] = useState(null);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const submitRepo = async () => {
    setIsSubmitted(true);
    const response = await axios.post("/api/repo/submit_repo", { repo_url: repoUrl });
    setRepoId(response.data.repo_id);
  };

  const { data: analysis, isFetching } = useQuery({
    queryKey: ["repo-analysis", repoId],
    queryFn: async () => {
      if (!repoId) return null;
      await new Promise((resolve) => setTimeout(resolve, 120000)); // Wait 2 mins
      const res = await axios.get(`/api/repo/get_repo/${repoId}`);
      return res.data;
    },
    enabled: !!repoId,
  });

  return (
    <div className="max-w-lg mx-auto mt-10 p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Submit Repository for Analysis</h2>
      <Input
        type="text"
        placeholder="Enter GitHub Repo URL"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
      />
      <Button onClick={submitRepo} className="mt-2">Submit</Button>
      
      {isSubmitted && (
        <p className="mt-4 text-gray-600">Analysis in progress... Please wait (~2 min).</p>
      )}

      {isFetching && <p className="mt-4 text-gray-600">Fetching analysis...</p>}

      {analysis && (
        <Card className="mt-4">
          <CardContent>
            <h3 className="text-lg font-semibold">Analysis Summary</h3>
            <p>{analysis.summary}</p>
            <h4 className="mt-4 font-semibold">Methods:</h4>
            <ul>
              {Object.entries(analysis.methods).map(([method, details]) => (
                <li key={method} className="mt-2">
                  <strong>{method}:</strong> {details.description} (Time: {details.time_complexity}, Space: {details.space_complexity})
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
