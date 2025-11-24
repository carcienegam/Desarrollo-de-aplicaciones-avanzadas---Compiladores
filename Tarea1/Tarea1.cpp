#include <iostream>
#include <stack>
#include <queue>
#include <unordered_map>

using namespace std;

// Stack LIFO
template <typename T>
class Stack{
private:
    stack<T> s;
public:
    // Inserts (or pushes) new element into the stack
    void push(T value){
        s.push(value);
    }

    // Deletes (or pops) the top element from the stack
    void pop(){
        if(!s.empty()){
            s.pop();
        } else {
            cout << "Stack is empty." << endl;
        }
    }

    // Returns the top element of the stack
    T top(){
        if(!s.empty()){
            return s.top();
        } else {
            cout << "Stack is empty." << endl;
            return T();
        }
    }

    // Checks if the stack is empty
    bool empty(){
        return s.empty();
    }

    // Returns the number of elements in the stack
    int size(){
        return s.size();
    }
};

// Queue FIFO
template <typename T>
class Queue{
private:
    queue<T> q;
public:
    // Inserts (or enqueues) new element into the queue
    void enqueue(T value){
        q.push(value);
    }

    // Deletes (or dequeues) the front element from the queue
    void dequeue(){
        if (!q.empty()){
            q.pop();
        }
        else {
            cout << "Queue is empty." << endl;
        }
    }

    // Returns the front element of the queue
    T front(){
        if (!q.empty()){
            return q.front();
        }
        else {
            cout << "Queue is empty." << endl;
            return T();
        }
    }

    // Returns the back element of the queue
    T back(){
        if (!q.empty()){
            return q.back();
        }
        else {
            cout << "Queue is empty." << endl;
            return T();
        }
    }

    // Checks if the queue is empty
    bool empty(){
        return q.empty();
    }

    // Returns the number of elements in the queue
    int size(){
        return q.size();
    }
};


class Dictionary{
private:
    unordered_map<string, int> dict;
public:
    // Insers a key and a value into the dictionary
    void insert(string k, int v){
        dict[k] = v;
    }
    
    // Returns the value paired with a key
    int get(string k){
        if (dict.find(k) != dict.end()){
            return dict[k];
        } else {
            cout << "Key not found." << endl;
            return -1;
        }
    }

    // Removes a key with its paired value
    void remove(string k){
        if (dict.find(k) != dict.end()){
            dict.erase(k);
        } else {
            cout << "Key not found." << endl;
        }
    }

    // Checks if a key exists
    bool exists(string k){
        return dict.find(k) != dict.end();
    }

    // Checks if the dictionary is empty
    bool empty(){
        return dict.empty();
    }

    // Returns the number of elements in the dictionary
    int size(){
        return dict.size();
    }
};

int main(){
    cout << "STACK (LIFO)" << endl;
    Stack<int> stack;
    stack.push(10);
    stack.push(20);
    stack.push(30);
    cout << "Top element: " << stack.top() << endl;
    cout << "Stack size: " << stack.size() << endl;
    stack.pop();
    cout << "Top element after pop: " << stack.top() << endl; 
    cout << "Stack size after pop: " << stack.size() << endl;

    cout << endl;
    cout << "QUEUE (FIFO)" << endl;
    Queue<int> queue;
    queue.enqueue(10);
    queue.enqueue(20);
    queue.enqueue(30);
    cout << "Front element: " << queue.front() << endl; 
    cout << "Back element: " << queue.back() << endl; 
    cout << "Queue size: " << queue.size() << endl;
    queue.dequeue();
    cout << "Front element after dequeue: " << queue.front() << endl; 
    cout << "Queue size after dequeue: " << queue.size() << endl;

    cout << endl;
    cout << "DICTIONARY (order)" << endl;
    Dictionary dict;
    dict.insert("one", 1);
    dict.insert("two", 2);
    dict.insert("three", 3);
    cout << "Value for key 'two': " << dict.get("two") << endl;
    cout << "Dictionary size: " << dict.size() << endl;
    dict.remove("two");
    cout << "Dictionary size after removal: " << dict.size() << endl;
    cout << "Exists key 'two': " << (dict.exists("two") ? "Yes" : "No") << endl; 

    return 0;
}