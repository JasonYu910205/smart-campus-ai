"use client";

import { FormEvent, useState } from "react";
import {
  askRag,
  retrieveRag,
  type RagAnswer,
  type RetrievedChunk,
} from "@/lib/api";

const examples = [
  "第一食堂冷藏柜 A03 出现 E03 故障，应该怎么处理？",
  "低压配电箱出现漏电报警如何安全处理？",
  "校园设备异常后如何创建工单？",
];

export function RagChat() {
  const [question, setQuestion] = useState(examples[0]);
  const [answer, setAnswer] = useState<RagAnswer | null>(null);
  const [chunks, setChunks] = useState<RetrievedChunk[]>([]);
  const [showChunks, setShowChunks] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setAnswer(null);
    setChunks([]);

    try {
      const [ragAnswer, retrieved] = await Promise.all([
        askRag(question),
        retrieveRag(question),
      ]);
      setAnswer(ragAnswer);
      setChunks(retrieved.chunks);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "RAG request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel flex min-h-[560px] flex-col p-6">
      <div className="mb-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-cyan-300 font-bold text-slate-950">
            AI
          </div>
          <div>
            <h2 className="font-medium text-white">设备维修知识助理</h2>
            <p className="text-xs text-emerald-300">
              ● Dense RAG · Qdrant · Source Citation
            </p>
          </div>
        </div>
        <a
          href="/rag-debug"
          className="text-xs text-cyan-300 hover:text-cyan-200"
        >
          RAG Debug →
        </a>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {examples.map((item) => (
          <button
            key={item}
            onClick={() => setQuestion(item)}
            className="rounded-full border border-slate-700 px-3 py-1.5 text-xs text-slate-400 hover:border-cyan-500/50 hover:text-cyan-200"
          >
            {item}
          </button>
        ))}
      </div>

      <div className="flex-1 rounded-2xl border border-slate-800 bg-slate-950/40 p-5">
        {!answer && !error && (
          <p className="text-sm leading-7 text-slate-400">
            问题会经过 Embedding、Qdrant 相似度检索和知识约束生成；回答引用来自实际
            Retriever metadata。
          </p>
        )}

        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">
            {error}
          </div>
        )}

        {answer && (
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-cyan-300">
              AI Answer
            </p>
            <p className="whitespace-pre-wrap text-sm leading-7 text-slate-200">
              {answer.answer}
            </p>
            <p className="mb-2 mt-6 text-xs font-semibold uppercase tracking-widest text-cyan-300">
              Sources
            </p>
            <div className="space-y-2">
              {answer.sources.map((source, index) => (
                <div
                  key={`${source.filename}-${source.chunk_index}-${index}`}
                  className="rounded-lg bg-slate-900 p-3 text-xs text-slate-400"
                >
                  <span className="text-slate-200">{source.filename}</span> ·
                  Chunk {source.chunk_index}
                  {source.page && ` · Page ${source.page}`} · Similarity{" "}
                  {source.score.toFixed(3)}
                </div>
              ))}
            </div>
          </div>
        )}

        {chunks.length > 0 && (
          <div className="mt-5 border-t border-slate-800 pt-4">
            <button
              onClick={() => setShowChunks((value) => !value)}
              className="text-sm text-cyan-300"
            >
              {showChunks ? "隐藏检索结果" : "查看检索结果"} ({chunks.length})
            </button>
            {showChunks && (
              <div className="mt-3 space-y-3">
                {chunks.map((chunk) => (
                  <article
                    key={`${chunk.document_id}-${chunk.chunk_index}`}
                    className="rounded-xl border border-slate-800 p-4"
                  >
                    <div className="mb-2 flex justify-between text-xs">
                      <span className="text-slate-300">
                        {chunk.filename} · Chunk {chunk.chunk_index}
                      </span>
                      <span className="text-emerald-300">
                        {chunk.score.toFixed(3)}
                      </span>
                    </div>
                    <p className="line-clamp-4 text-xs leading-6 text-slate-500">
                      {chunk.text}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <form onSubmit={submit} className="mt-4 flex gap-3">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="询问设备故障或维修 SOP…"
          className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm outline-none focus:border-cyan-400"
        />
        <button
          disabled={loading}
          className="rounded-xl bg-cyan-300 px-5 font-medium text-slate-950 disabled:opacity-50"
        >
          {loading ? "检索中…" : "发送"}
        </button>
      </form>
    </section>
  );
}
