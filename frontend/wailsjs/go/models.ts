export namespace env {
	
	export class ApplyResult {
	    applied: string[];
	    message: string;
	    method: string;
	
	    static createFrom(source: any = {}) {
	        return new ApplyResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.applied = source["applied"];
	        this.message = source["message"];
	        this.method = source["method"];
	    }
	}

}

export namespace mcp {
	
	export class ListResult {
	    tools: any[];
	    resources: any[];
	
	    static createFrom(source: any = {}) {
	        return new ListResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.tools = source["tools"];
	        this.resources = source["resources"];
	    }
	}
	export class TestResult {
	    success: boolean;
	    message?: string;
	    error?: string;
	    serverInfo?: Record<string, any>;
	
	    static createFrom(source: any = {}) {
	        return new TestResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.success = source["success"];
	        this.message = source["message"];
	        this.error = source["error"];
	        this.serverInfo = source["serverInfo"];
	    }
	}

}

export namespace skills {
	
	export class Skill {
	    name: string;
	    description: string;
	    context: string;
	    agent: string;
	    allowed_tools: string;
	    argument_hint: string;
	    user_invocable: boolean;
	    disable_model_invocation: boolean;
	    path: string;
	    scope: string;
	    content: string;
	    frontmatter: Record<string, any>;
	
	    static createFrom(source: any = {}) {
	        return new Skill(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.description = source["description"];
	        this.context = source["context"];
	        this.agent = source["agent"];
	        this.allowed_tools = source["allowed_tools"];
	        this.argument_hint = source["argument_hint"];
	        this.user_invocable = source["user_invocable"];
	        this.disable_model_invocation = source["disable_model_invocation"];
	        this.path = source["path"];
	        this.scope = source["scope"];
	        this.content = source["content"];
	        this.frontmatter = source["frontmatter"];
	    }
	}

}

