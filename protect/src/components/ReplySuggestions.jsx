import { useSelector } from 'react-redux';

function ReplySuggestions() {
  const messages = useSelector((state) => state.workDefense.result.messages);

  return (
    <section className="panel" aria-labelledby="reply-title">
      <div className="section-heading">
        <p className="eyebrow">Step 3</p>
        <h2 id="reply-title">팀장님께 보내는 추천 답변</h2>
      </div>
      <div className="reply-list">
        {messages.map((message) => (
          <blockquote key={message}>{message}</blockquote>
        ))}
      </div>
    </section>
  );
}

export default ReplySuggestions;
