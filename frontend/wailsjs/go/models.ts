export namespace codex {
	
	export class Profile {
	    name: string;
	    model: string;
	    provider: string;
	    hasConfig: boolean;
	    hasModels: boolean;
	    active: boolean;
	
	    static createFrom(source: any = {}) {
	        return new Profile(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.model = source["model"];
	        this.provider = source["provider"];
	        this.hasConfig = source["hasConfig"];
	        this.hasModels = source["hasModels"];
	        this.active = source["active"];
	    }
	}
	export class ListResult {
	    dir: string;
	    exists: boolean;
	    profiles: Profile[];
	    active: string;
	    activeModel: string;
	    catalogPath: string;
	
	    static createFrom(source: any = {}) {
	        return new ListResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.dir = source["dir"];
	        this.exists = source["exists"];
	        this.profiles = this.convertValues(source["profiles"], Profile);
	        this.active = source["active"];
	        this.activeModel = source["activeModel"];
	        this.catalogPath = source["catalogPath"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	
	export class SwitchResult {
	    active: string;
	    message: string;
	    syncedFrom: string;
	    backedUp: string[];
	    warning?: string;
	
	    static createFrom(source: any = {}) {
	        return new SwitchResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.active = source["active"];
	        this.message = source["message"];
	        this.syncedFrom = source["syncedFrom"];
	        this.backedUp = source["backedUp"];
	        this.warning = source["warning"];
	    }
	}

}

export namespace config {
	
	export class ApplyResult {
	    applied: string[];
	    message: string;
	    path: string;
	
	    static createFrom(source: any = {}) {
	        return new ApplyResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.applied = source["applied"];
	        this.message = source["message"];
	        this.path = source["path"];
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

