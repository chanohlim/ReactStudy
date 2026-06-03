import { useOptimistic, useState, useRef } from 'react';

async function deliverMessage(message) {
  await new Promise((res) => setTimeout(res, 1000));
  return message;
}

function Thread({ messages, sendMessage }){ // props 구조할당
  const formRef = useRef();
  const inputRef = useRef();

  async function formAction(formData) {
    addOptimisticMessage(formData.get("message"));
    formRef.current.reset();
    await sendMessage(formData);
    inputRef.current.focus();
  }

  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    messages,
    (state, newMessage) => [
      ...state,
      {
        text: newMessage,
        sending: true
      }
    ]
  );

  return(<>
    {optimisticMessages.map((message, index) => (
      <div key={index}>
        {message.text}
        {!!message.sending && <small> (Sending...)</small>}
      </div>
    ))}
    <form action={formAction} ref={formRef}>
      <input type="text" name="message" placeholder='메시지를 입력해주세요' ref={inputRef}/>
      <button type="submit">Send</button>
    </form>
  </>);
}

const UseOptimisticExam = () => {
  const [messages, setMessages] = useState([
    { text: "기본 메시지 입니다", sending: false, key: 1}
  ]);

  async function sendMessage(formData) {
    const sentMessage = await deliverMessage(formData.get("message"));
    setMessages((messages) => [...messages, { text: sentMessage }]);
  }

  return(<>
    <div>
      <h2>useOptimistic 사용하기</h2>
      <Thread messages={messages} sendMessage={sendMessage} />
    </div>
  </>);
};

export default UseOptimisticExam;