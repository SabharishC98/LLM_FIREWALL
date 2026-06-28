class FirewallBlockedError extends Error {
  constructor(message, report) {
    super(message);
    this.name = "FirewallBlockedError";
    this.report = report;
    
    // Maintain proper stack trace in V8 engines (Node.js)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }
}

module.exports = {
  FirewallBlockedError,
};
