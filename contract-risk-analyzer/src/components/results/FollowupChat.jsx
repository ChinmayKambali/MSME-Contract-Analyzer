import { useState } from "react";
import { MessageSquare, Send, Loader2, Bot, User } from "lucide-react";
import { useContract } from "../../context/ContractContext";
import { postFollowupChat } from "../../utils/apiClient";

export default function FollowupChat() {
  const { contract } = useContract();
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "I have analyzed this contract. Ask me any follow-up questions about clauses, payment terms, or legal risks!",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const handleSend = async (messageText = input) => {
    const textToSend = messageText.trim();
    if (!textToSend || sending) return;

    const userMsg = { sender: "user", text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSending(true);

    try {
      if (contract.analysisId) {
        const res = await postFollowupChat(contract.analysisId, textToSend);
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: res.reply || "No reply generated." },
        ]);
      } else {
        // Demo fallback
        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",
            text: "Based on the analyzed contract, payment terms require settlement within the specified credit period, and liability is capped as per Section 11.",
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: `Follow-up chat error: ${err.message || "Unable to reach assistant."}`,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const suggestions = [
    "What are the payment terms and interest clauses?",
    "Is supplier liability capped or uncapped?",
    "What is the notice period for termination?",
  ];

  return (
    <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
      <div className="mb-4 flex items-center gap-2 text-[#163b43]">
        <MessageSquare size={20} className="text-[#d97745]" />
        <h3 className="text-lg font-bold">Ask Follow-up Questions</h3>
      </div>

      <div className="mb-4 max-h-72 space-y-3 overflow-y-auto rounded-xl bg-slate-50 p-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex gap-3 text-sm ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.sender === "bot" && (
              <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[#163b43] text-white">
                <Bot size={14} />
              </span>
            )}
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 leading-relaxed ${
                msg.sender === "user"
                  ? "bg-[#3b8c80] text-white rounded-br-none"
                  : "bg-white text-slate-800 border border-slate-200 shadow-xs rounded-bl-none"
              }`}
            >
              {msg.text}
            </div>
            {msg.sender === "user" && (
              <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[#d97745] text-white">
                <User size={14} />
              </span>
            )}
          </div>
        ))}

        {sending && (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Loader2 size={14} className="animate-spin text-[#d97745]" /> Assistant is thinking...
          </div>
        )}
      </div>

      {messages.length < 3 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(s)}
              className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 transition hover:bg-[#fff1e9] hover:text-[#d97745]"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this contract..."
          className="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm outline-none transition focus:border-[#3b8c80] focus:ring-1 focus:ring-[#3b8c80]"
        />
        <button
          type="submit"
          disabled={!input.trim() || sending}
          className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#163b43] text-white transition hover:bg-[#204f5a] disabled:opacity-50"
        >
          {sending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
        </button>
      </form>
    </div>
  );
}
